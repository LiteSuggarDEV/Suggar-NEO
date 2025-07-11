import uuid
from uuid import uuid5

SUGGAR_VALUE_ID = uuid5(uuid.NAMESPACE_X500, "original").hex
SUGGAR_EXP_ID = uuid5(uuid.NAMESPACE_X500, "exp").hex
