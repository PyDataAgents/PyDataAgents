# + Buffer Documentation

## `DictBuffer` (from `DictBuffer.py`)

buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
    
_No fields defined._

## `ListBuffer` (from `ListBuffer.py`)

buffer that stores its values in a capacity limited list
    
_No fields defined._

## `SampledBuffer` (from `SampledBuffer.py`)

A buffer that samples a signal at a specified interval.
_No fields defined._

## `SignalBuffer` (from `SignalBuffer.py`)

A buffer that holds signals with a specific start time and elapsed time.

Attributes:
    start_time (int): The start time of the signal in milliseconds.
    elapsed_time (float): The elapsed time since the start in seconds.
| Field | Type | Description |
|-------|------|-------------|
| `signal` | `Signal` | a signal object to simulate data |
| `sampling_period` | `int` | interval in milliseconds for update |

## `TimedBuffer` (from `TimedBuffer.py`)

A buffer that stores data with timestamps.
Inherits from ListBuffer.
_No fields defined._

## `TransformsBuffer` (from `TransformsBuffer.py`)

TransformsBuffer is a subclass of ListBuffer that allows for data transformation.
It is used to transform data from one format to another.
| Field | Type | Description |
|-------|------|-------------|
| `transformations` | `list[ObjectTransformation]` | List of transformations to apply to the data |
