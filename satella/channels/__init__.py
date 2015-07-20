from satella.channels.exceptions import ChannelException, FatalException, NonfatalException, \
                                        ChannelClosed, ChannelFailure, DataNotAvailable, \
                                        InvalidOperation, TransientFailure
from satella.channels.base import Channel, HandlingLayer
from satella.channels.subtypes import LockSignalledChannel, FileDescriptorChannel