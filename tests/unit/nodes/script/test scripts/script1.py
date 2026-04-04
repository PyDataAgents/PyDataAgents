# this is a script for a ScriptAction
import numpy as np

ar = np.array(values)  # values must be an input key of the ScriptAction

rms = float(np.sqrt(np.mean(ar**2))) # rms is only written to the buffer if it is specified as an output_key of the ScriptAction, otherwise it will not be stored in the buffer and not be accessible for other nodes. The same applies for mean.
mean = float(np.mean(ar)) # mean is only written to the buffer if it is specified as an output_key of the ScriptAction, otherwise it will not be stored in the buffer and not be accessible for other nodes. The same applies for rms.
