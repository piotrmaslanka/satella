import typing as tp
import multiprocessing
import warnings

__all__ = ['monkey_patch_parallel_compilation']

# shamelessly ripped from
# https://stackoverflow.com/questions/11013851/speeding-up-build-process-with-distutils
# with some changes introduced by me


def monkey_patch_parallel_compilation(cores: tp.Optional[int] = None) -> None:
    """
    This monkey-patches distutils to provide parallel compilation, even if you have
    a single extension built from multiple .c files.

    Invoke in your setup.py file

    :param cores: amount of cores. Leave at default (None) for autodetection.
    """
    if cores is None:
        cores = multiprocessing.cpu_count()

    # monkey-patch for parallel compilation
    def parallelCCompile(self, sources, output_dir=None, macros=None, include_dirs=None, debug=0,
                         extra_preargs=None, extra_postargs=None, depends=None):
        # those lines are copied from distutils.ccompiler.CCompiler directly
        macros, objects, extra_postargs, pp_opts, build = self._setup_compile(output_dir, macros,
                                                                              include_dirs, sources,
                                                                              depends,
                                                                              extra_postargs)
        cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
        # parallel code
        import multiprocessing.pool

        def single_compile(obj):
            try:
                src, ext = build[obj]
            except KeyError:
                return
            self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)

        # evaluate everything
        for _ in multiprocessing.pool.ThreadPool(cores).imap(single_compile, objects):
            pass
        return objects

    import distutils.ccompiler
    distutils.ccompiler.CCompiler.compile = parallelCCompile
    warnings.warn('This function remains experimental and is likely to be moved into snakehouse',
                  UserWarning)
