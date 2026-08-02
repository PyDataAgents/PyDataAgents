# Actions and Transitions Documentation

## Summary

| Class | Description | Icon |
|-------|-------------|------|
| [`Action`](#action-in-pydagnodesactionpy) |  | ![Action](element_icons/Action.png)
| [`AgentNode`](#agentnode-in-pydagnodesagentnodepy) |  | ![AgentNode](element_icons/AgentNode.png)
| [`BufferNode`](#buffernode-in-pydagnodesbuffernodepy) |  | ![BufferNode](element_icons/BufferNode.png)
| [`LearningNode`](#learningnode-in-pydagnodeslearningnodepy) | LearningNode is a base class for elements that require a learning step in their pipeline execution.It extends the BufferNode class and provides additional functionality specific to learning tasks. | ![LearningNode](element_icons/LearningNode.png)
| [`Node`](#node-in-pydagnodesnodepy) |  | ![Node](element_icons/Node.png)
| [`ServiceNode`](#servicenode-in-pydagnodesservicenodepy) | A class representing a service node in a state machine.Inherits from Node and adds functionality specific to service nodes. | ![ServiceNode](element_icons/ServiceNode.png)
| [`Transition`](#transition-in-pydagnodestransitionpy) | A `Transition` `Node` that defines conditions for state transitions in a state machine.     | ![Transition](element_icons/Transition.png)
| [`TriggerAction`](#triggeraction-in-pydagnodestriggeractionpy) | Abstract `Action` `Node`that defines the interface for `Node`s with trigger logic, that are not executed directly within a `StatemachineService`,but are rather started from external events and trigger the execution `StatemachineService`. | ![TriggerAction](element_icons/TriggerAction.png)
| [`AddBufferAction`](#addbufferaction-in-pydagnodesbuffersaddbufferactionpy) | Action to add a buffer to the agent node. | ![AddBufferAction](element_icons/AddBufferAction.png)
| [`BufferEmptyTransition`](#bufferemptytransition-in-pydagnodesbuffersbufferemptytransitionpy) | A transition that checks if specified buffer is empty.If the buffer is empty, the transition is successful. | ![BufferEmptyTransition](element_icons/BufferEmptyTransition.png)
| [`BufferExtractAction`](#bufferextractaction-in-pydagnodesbuffersbufferextractactionpy) | `Action` for extracting data from a specified buffer and to store the extracted data into this buffer.This `Action` can only be applied on if the specified buffer is of type `DictBuffer`. | ![BufferExtractAction](element_icons/BufferExtractAction.png)
| [`BufferInRangeTransition`](#bufferinrangetransition-in-pydagnodesbuffersbufferinrangetransitionpy) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. | ![BufferInRangeTransition](element_icons/BufferInRangeTransition.png)
| [`BufferNotEmptyTransition`](#buffernotemptytransition-in-pydagnodesbuffersbuffernotemptytransitionpy) | A transition that checks if specified buffer is not empty.If the buffer is not empty, the transition is successful. | ![BufferNotEmptyTransition](element_icons/BufferNotEmptyTransition.png)
| [`ClearBufferAction`](#clearbufferaction-in-pydagnodesbuffersclearbufferactionpy) |  | ![ClearBufferAction](element_icons/ClearBufferAction.png)
| [`CompareBufferTransition`](#comparebuffertransition-in-pydagnodesbufferscomparebuffertransitionpy) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. | ![CompareBufferTransition](element_icons/CompareBufferTransition.png)
| [`CopyBufferAction`](#copybufferaction-in-pydagnodesbufferscopybufferactionpy) | `Action` that copies the entire parent buffer to this `Node`'s `Buffer` whenever executed.The copy procedure makes a deep of all the parent's `Buffer` elements | ![CopyBufferAction](element_icons/CopyBufferAction.png)
| [`CopyDataAction`](#copydataaction-in-pydagnodesbufferscopydataactionpy) | `Action` that makes a copy of the data in all parent `Buffer`s found amongst this `Node`s parents.If this `Node`'s parents contains more than one `BufferNode`, all data is merged and copied.Before this `Node`s `Buffer` is filled, all other elements are cleared. | ![CopyDataAction](element_icons/CopyDataAction.png)
| [`DataFrameFilterAction`](#dataframefilteraction-in-pydagnodesbuffersdataframefilteractionpy) |  | ![DataFrameFilterAction](element_icons/DataFrameFilterAction.png)
| [`DataToBuffersAction`](#datatobuffersaction-in-pydagnodesbuffersdatatobuffersactionpy) | `Action` that copies data of the `Buffer` specified via `buffer_id` or found in the first `BufferNode` found amongst this `Node`s parents to all the buffers specified via `buffer_ids`.If this `Node`'s parents contain more than one `BufferNode`, only the first is respected. | ![DataToBuffersAction](element_icons/DataToBuffersAction.png)
| [`FormatBufferColumnAction`](#formatbuffercolumnaction-in-pydagnodesbuffersformatbuffercolumnactionpy) |  | ![FormatBufferColumnAction](element_icons/FormatBufferColumnAction.png)
| [`FormattedStringAction`](#formattedstringaction-in-pydagnodesbuffersformattedstringactionpy) | `Action` to compose a formatted string and store it in this `Action`'s bufferusing its parent's buffer to create the new string | ![FormattedStringAction](element_icons/FormattedStringAction.png)
| [`LinkBufferAction`](#linkbufferaction-in-pydagnodesbufferslinkbufferactionpy) | `Action` that's only function is to link a buffer from agent to the statemachinetherefore an empty execute method is provided | ![LinkBufferAction](element_icons/LinkBufferAction.png)
| [`SampledSignalAction`](#sampledsignalaction-in-pydagnodesbufferssampledsignalactionpy) |  | ![SampledSignalAction](element_icons/SampledSignalAction.png)
| [`ShiftMonitoring`](#shiftmonitoring-in-pydagnodesclusteringshiftmonitoringpy) | ShiftMonitoring is a LearningNode that monitors distributional shifts in incoming data. It uses statistical methods to compare the distribution of new data against learned distributions and can identify when a significant shift occurs.Returns the deviation as well as the outlier-decision to the first distribution "A", even if n_distributions > 2. | ![ShiftMonitoring](element_icons/ShiftMonitoring.png)
| [`PivotAction`](#pivotaction-in-pydagnodesdbpivotactionpy) | Args:    BufferNode (_type_): _description_    Action (_type_): _description_ | ![PivotAction](element_icons/PivotAction.png)
| [`SQLAction`](#sqlaction-in-pydagnodesdbsqlactionpy) | `Action` node to perform SQL operations using the pyodbc library.     | ![SQLAction](element_icons/SQLAction.png)
| [`IsomapDimReduction`](#isomapdimreduction-in-pydagnodesdimreductionisomapdimreductionpy) | Dimensionality reduction using Isomap algorithm. Mind, that the Algorithms is trained on two dimensional data with shape (n_samples, n_features). Hence sample_length should be larger than the number of dimensions.  | ![IsomapDimReduction](element_icons/IsomapDimReduction.png)
| [`LocallyLinearEmbeddingsReduction`](#locallylinearembeddingsreduction-in-pydagnodesdimreductionlocallylinearembeddingsreductionpy) | Dimensionality reduction using LocallyLinearEmbeddings algorithm. Mind, that the Algorithms is trained on two dimensional data with shape (n_samples, n_features). Hence sample_length should be larger than the number of dimensions.  | ![LocallyLinearEmbeddingsReduction](element_icons/LocallyLinearEmbeddingsReduction.png)
| [`PCADimReduction`](#pcadimreduction-in-pydagnodesdimreductionpcadimreductionpy) | Dimensionality reduction using PCA algorithm. Mind, that the Algorithms is trained on two dimensional data with shape (n_samples, n_features). Hence sample_length should be larger than the number of dimensions.  | ![PCADimReduction](element_icons/PCADimReduction.png)
| [`CompressAction`](#compressaction-in-pydagnodesdocumentscompressactionpy) | `Action` that converts the specified `source_file` to compressed archive file under the new filepath `target_file`         | ![CompressAction](element_icons/CompressAction.png)
| [`ConvertFile2Base64Action`](#convertfile2base64action-in-pydagnodesdocumentsconvertfile2base64actionpy) |  | ![ConvertFile2Base64Action](element_icons/ConvertFile2Base64Action.png)
| [`CopyFilesAction`](#copyfilesaction-in-pydagnodesdocumentscopyfilesactionpy) |  | ![CopyFilesAction](element_icons/CopyFilesAction.png)
| [`DecompressAction`](#decompressaction-in-pydagnodesdocumentsdecompressactionpy) | `Action` that decompresses the specified `source_file` under the new filepath `target_dir`         | ![DecompressAction](element_icons/DecompressAction.png)
| [`DocxTemplateAction`](#docxtemplateaction-in-pydagnodesdocumentsdocxtemplateactionpy) | `Action` for writing data to DOCX template document.buffers of parent elements can be used to populate the docx file, if `buffer_id` or `set_buffer(...)` is specified then only this buffer is used | ![DocxTemplateAction](element_icons/DocxTemplateAction.png)
| [`HTMLFileAction`](#htmlfileaction-in-pydagnodesdocumentshtmlfileactionpy) |  | ![HTMLFileAction](element_icons/HTMLFileAction.png)
| [`HTMLTableAction`](#htmltableaction-in-pydagnodesdocumentshtmltableactionpy) | This `BufferNode` creates a HTML Table string based on the parent data input to this `Node`.By default it outputs the HTML to a key named 'html' for child `Node`s to consume. | ![HTMLTableAction](element_icons/HTMLTableAction.png)
| [`ICalAction`](#icalaction-in-pydagnodesdocumentsicalactionpy) |  | ![ICalAction](element_icons/ICalAction.png)
| [`ListFilesAction`](#listfilesaction-in-pydagnodesdocumentslistfilesactionpy) |  | ![ListFilesAction](element_icons/ListFilesAction.png)
| [`MoveFilesAction`](#movefilesaction-in-pydagnodesdocumentsmovefilesactionpy) | `Action` that moves files to a new `target_folder`<br>this `Action` either needs a parent `Node` with a `ListBuffer` with filepaths or a reference to a `Buffer` via `buffer_id` or its `buffer`variableRaises:    StatemachineException: if folder does not exist or wrong `Buffer` is provided | ![MoveFilesAction](element_icons/MoveFilesAction.png)
| [`PDFReadFormAction`](#pdfreadformaction-in-pydagnodesdocumentspdfreadformactionpy) | Extract context-rich AcroForm fields from PDF files using PyMuPDF. | ![PDFReadFormAction](element_icons/PDFReadFormAction.png)
| [`PDFWriteFormAction`](#pdfwriteformaction-in-pydagnodesdocumentspdfwriteformactionpy) | Write LLM- or user-provided values into PDF AcroForm fields using PyMuPDF. | ![PDFWriteFormAction](element_icons/PDFWriteFormAction.png)
| [`PlotlifyAction`](#plotlifyaction-in-pydagnodesdocumentsplotlifyactionpy) | `Action` that generates a plotly file based on the data and layout specified and extracted from the specified buffer or its parents `Buffer`s.     | ![PlotlifyAction](element_icons/PlotlifyAction.png)
| [`ReadCsvAction`](#readcsvaction-in-pydagnodesdocumentsreadcsvactionpy) |  | ![ReadCsvAction](element_icons/ReadCsvAction.png)
| [`ReadExcelRangeAction`](#readexcelrangeaction-in-pydagnodesdocumentsreadexcelrangeactionpy) | This `Action` reads data from specified workbook, worksheet and rangeArgs:    BufferNode (_type_): _description_    Action (_type_): _description_Raises:    NodeException: _description_ | ![ReadExcelRangeAction](element_icons/ReadExcelRangeAction.png)
| [`ReadExcelTableAction`](#readexceltableaction-in-pydagnodesdocumentsreadexceltableactionpy) |  | ![ReadExcelTableAction](element_icons/ReadExcelTableAction.png)
| [`ReadExcelWorksheetAction`](#readexcelworksheetaction-in-pydagnodesdocumentsreadexcelworksheetactionpy) | This `BufferNode` reads the entire content of a specified Excel worksheet into a buffer.It automatically detects the first worksheet with data if no specific worksheet is specified,finds the connected range of data, and uses the first row as headers by default.Args:    BufferNode: Provides buffer management functionality    Action: Provides action execution framework    Raises:    NodeException: If file not found, worksheet not found, or no data found in worksheet | ![ReadExcelWorksheetAction](element_icons/ReadExcelWorksheetAction.png)
| [`ReadJsonAction`](#readjsonaction-in-pydagnodesdocumentsreadjsonactionpy) |  | ![ReadJsonAction](element_icons/ReadJsonAction.png)
| [`ReadNpzAction`](#readnpzaction-in-pydagnodesdocumentsreadnpzactionpy) |  | ![ReadNpzAction](element_icons/ReadNpzAction.png)
| [`ReadPDFFormAction`](#readpdfformaction-in-pydagnodesdocumentsreadpdfformactionpy) | `Action` that extracts AcroForm fields and text from PDFs.Limitation:This action only extracts native PDF AcroForm data. PDFs without AcroForm fieldsreturn an empty `fields` list. | ![ReadPDFFormAction](element_icons/ReadPDFFormAction.png)
| [`ReadXMLAction`](#readxmlaction-in-pydagnodesdocumentsreadxmlactionpy) |  | ![ReadXMLAction](element_icons/ReadXMLAction.png)
| [`WritePDFFormAction`](#writepdfformaction-in-pydagnodesdocumentswritepdfformactionpy) | `Action` that writes form values into parent-provided PDF files. | ![WritePDFFormAction](element_icons/WritePDFFormAction.png)
| [`CNN1DAutoencoder`](#cnn1dautoencoder-in-pydagnodesfeatureextractioncnn1dautoencoderpy) | This `DataElement` represents a time series feature extraction model using a 1D CNN Autoencoder. | ![CNN1DAutoencoder](element_icons/CNN1DAutoencoder.png)
| [`ChronosExtractor`](#chronosextractor-in-pydagnodesfeatureextractionchronosextractorpy) | Chronos Extractor for time series data. Returns 384-dimensional embeddings for each input time series sample using a pretrained Chronos model. | ![ChronosExtractor](element_icons/ChronosExtractor.png)
| [`PSDExtractor`](#psdextractor-in-pydagnodesfeatureextractionpsdextractorpy) | PSD for time series data. Returns 261-dimensional embeddings for each input time series sample using the Welch method from https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html.257 frequency bins + peak frequency + peak power + mean power + std power = 261 features per time series sample. | ![PSDExtractor](element_icons/PSDExtractor.png)
| [`RIFEExtractor`](#rifeextractor-in-pydagnodesfeatureextractionrifeextractorpy) | Random Interval Feature Extractor for time series data.Produces a 320 dimensional feature vector per input time series sample usingsktime's RandomIntervalFeatureExtractor with:    - n_intervals = 64    - features = [np.median, np.std, iqr, np.min, np.max]yielding 64 * 5 = 320 features. Deterministic with random_state=42.Notes:    - No learning required (pure feature extraction).    - Accepts input dictionary with one or multiple keys; each key's value must      be a 1D array-like time series. Generates a single feature vector per key.    - Output keys follow the pattern: "<orig_key>-feature-rife-<i>" where i is the      index (0..255) of the feature.    - The extractor samples random start–end pairs. Depending on the sktime version, intervals that are invalid (e.g. zero or 1-length after an internal constraint) can get skipped. In such cases, the output feature vector is zero-padded to 320 length. | ![RIFEExtractor](element_icons/RIFEExtractor.png)
| [`ROCKETExtractor`](#rocketextractor-in-pydagnodesfeatureextractionrocketextractorpy) | ROCKET feature extractor.https://www.sktime.net/en/stable/api_reference/auto_generated/sktime.transformations.panel.rocket.Rocket.html | ![ROCKETExtractor](element_icons/ROCKETExtractor.png)
| [`TirexExtractor`](#tirexextractor-in-pydagnodesfeatureextractiontirexextractorpy) | This `DataElement` represents a time series feature extraction model using the TiREx framework.Read: https://github.com/NX-AI/tirexfor more information. | ![TirexExtractor](element_icons/TirexExtractor.png)
| [`HttpGetAction`](#httpgetaction-in-pydagnodeshttphttpgetactionpy) |  | ![HttpGetAction](element_icons/HttpGetAction.png)
| [`HttpPostAction`](#httppostaction-in-pydagnodeshttphttppostactionpy) |      | ![HttpPostAction](element_icons/HttpPostAction.png)
| [`HttpPutAction`](#httpputaction-in-pydagnodeshttphttpputactionpy) |      | ![HttpPutAction](element_icons/HttpPutAction.png)
| [`HuggingFaceAction`](#huggingfaceaction-in-pydagnodesllmhuggingfaceactionpy) |  | ![HuggingFaceAction](element_icons/HuggingFaceAction.png)
| [`LLMChatAction`](#llmchataction-in-pydagnodesllmllmchatactionpy) | `Action` to chat with a `RAGService` and store the response in its `Buffer`.Usage modes:1. Chat-Only: (default) `RAGService` with `use_rag_context=False`, only `question`.2. Chat-with-RAG-context: `RAGService` with `question`, retrieval enabled.3. Chat-with-local-context: `RAGService` with `question` + `input_context`, `use_rag_context=False`.4. Full-mode-augment: `question` + `input_context` + retrieval enabled, no strict structure enforcement.5. Full-mode-template_fill: same as full augment plus strict structure validation.Optional file context can be supplied via `context_files_key` or `context_files_value`. V1 accepts external URLs, local file URLs, local paths absolute or relative to the current working directory, data URIs, plain base64 strings, raw bytes, or lists of those values. File inputs are supported only for OPENAI and AZURE model providers. OLLAMA file processing is not implemented yet; supplying files with OLLAMA emits a warning and continues text-only. | ![LLMChatAction](element_icons/LLMChatAction.png)
| [`LLMImageAnalysisAction`](#llmimageanalysisaction-in-pydagnodesllmllmimageanalysisactionpy) | `Action` to retrieve information from an image and store the response in its `Buffer`.The Action analyses arbitrary images for its content (not only text documents like OCR). Hence it is powerful for image understanding tasks. If you specifically want to extract text as well as its formatting from images, consider using the LLMOCRAction instead.The parent Buffer Node is expected to provide file paths to images or PDFs.The allowed inpus formats for the file paths are:- A fully qualified file path as a string- an image as a Base64-encoded data URL - For OpanAI models: a file ID (created with the Files API (https://platform.openai.com/docs/api-reference/files))The OpenAI API is used.Keep in mind that the provided model must support image inputs, e.g. for OpenAI use "gpt-4o" or "gpt-4o-mini" or "gpt-4.1-mini" or "gpt-4.1" or "gpt-5".For more models and providers refer to their documentation, e.g. OpenAI: https://platform.openai.com/docs/models".The output has the following format:{    "question": <the question asked>,    "answer": <the answer from the LLM>    "filepath": <file path for each processed input>} | ![LLMImageAnalysisAction](element_icons/LLMImageAnalysisAction.png)
| [`LLMOCRAction`](#llmocraction-in-pydagnodesllmllmocractionpy) | `Action` to retrieve text from an image or PDF and store the extracted text in its `Buffer`.The parent Buffer Node is expected to provide file paths to images or PDFs.The allowed input formats for the file paths are:- A fully qualified file path as a string- an image as a Base64-encoded data URL The Mistral OCR-3 model is used to extract text from the images or PDFs.For more information about the Mistral OCR-3 model: https://mistral.ai/news/mistral-ocr-3".The output has the following format:{    "documents": <String of extracted text pages creatred from the contents of the origial OCRPageObject returned by Mistral>,    "filepath": <file path for each processed input>}Where the original OCRPageObject has the following format:    {    "pages": [ # The content of each page        {        "index": int, # The index of the corresponding page        "markdown": str, # The main output and raw markdown content        "images": list, # Image information when images are extracted        "tables": list, # Table information when using `table_format=html`        "hyperlinks": list, # Hyperlinks detected        "header": str|null, # Header content when using `extract_header=True`        "footer": str|null, # Footer content when using `extract_footer=True`        "dimensions": dict # The dimensions of the page        }    ],    "model": str, # The model used for the OCR    "document_annotation": dict|null, # Document annotation information when used, visit the Annotations documentation for more information    "usage_info": dict # Usage information    }See https://docs.mistral.ai/capabilities/document_ai/basic_ocr for more details. | ![LLMOCRAction](element_icons/LLMOCRAction.png)
| [`LLMScriptElement`](#llmscriptelement-in-pydagnodesllmllmscriptelementpy) | `DataElement` to generate Code for data processing using LLM on a specified input     | ![LLMScriptElement](element_icons/LLMScriptElement.png)
| [`FFTTransform`](#ffttransform-in-pydagnodespreprocessingfrequencyffttransformpy) |  | ![FFTTransform](element_icons/FFTTransform.png)
| [`ZScore`](#zscore-in-pydagnodespreprocessingstatisticszscorepy) |  | ![ZScore](element_icons/ZScore.png)
| [`TrendWindowNode`](#trendwindownode-in-pydagnodespreprocessingwindowingtrendwindownodepy) | This `BufferNode` collects windowed data of the linked parents of specified size `n` with the current timestamp as key prefix to the original key.Whenever it is executed it generates a new window to keep (up to `max_windows`). If the maximum number of windows are reached, it discards the one closest to any other window, based on timestamp.Base Classes:    BufferNode (_type_): _description_    Action (_type_): _description_ | ![TrendWindowNode](element_icons/TrendWindowNode.png)
| [`RegressionTransform`](#regressiontransform-in-pydagnodesregressionregressiontransformpy) | Code Service to do Regression on Inputs     | ![RegressionTransform](element_icons/RegressionTransform.png)
| [`ScriptAction`](#scriptaction-in-pydagnodesscriptscriptactionpy) | `Action` for executing a custom script to process data from the parents' `Buffer`s and to store the processed data back into this `Buffer`.<br>The script must be a valid Python code snippet that runs properly.<br>The function takes the current buffer data and injects data from it by the specified `input_keys`.<br>The same way the `Action`returns data by the specified `output_keys` back to its `Buffer`.<br>Note that the script is executed in its own local scope, so variables defined in the script do not interfere with variables outside the script.<br>Also note that all output variables should be converted to primitives (e.g. int, float, str, list, dict) or list of primitives inside the script. Do not leave them as numpy arrays or dataframes. | ![ScriptAction](element_icons/ScriptAction.png)
| [`FileTriggerAction`](#filetriggeraction-in-pydagnodestriggersfiletriggeractionpy) |  | ![FileTriggerAction](element_icons/FileTriggerAction.png)
| [`ObserverTriggerAction`](#observertriggeraction-in-pydagnodestriggersobservertriggeractionpy) | A `TriggerAction`, that connects to a `ObserverService` and executes the `Observer` notification everytime thetrigger event occurs. This `Node` does not define `start_trigger`, but rather expects being triggered externally from application or for example REST API. | ![ObserverTriggerAction](element_icons/ObserverTriggerAction.png)
| [`ConfigureElementAction`](#configureelementaction-in-pydagnodesutilsconfigureelementactionpy) | this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property<br>the new property value is derived from the `Node`'s `buffer`Args:    GrabberNode (_type_): inherits from class GrabberNode    BufferNode (_type_): inherits from class BufferNodeRaises:    StatemachineException: if an error occurs during execute | ![ConfigureElementAction](element_icons/ConfigureElementAction.png)
| [`CountAction`](#countaction-in-pydagnodesutilscountactionpy) | Action that counts the number of times it has been called. | ![CountAction](element_icons/CountAction.png)
| [`CountTransition`](#counttransition-in-pydagnodesutilscounttransitionpy) | A transition that counts the number of times it has been triggered. | ![CountTransition](element_icons/CountTransition.png)
| [`FalseTransition`](#falsetransition-in-pydagnodesutilsfalsetransitionpy) | A transition that always returns False. | ![FalseTransition](element_icons/FalseTransition.png)
| [`JoinTransition`](#jointransition-in-pydagnodesutilsjointransitionpy) |  | ![JoinTransition](element_icons/JoinTransition.png)
| [`MailAction`](#mailaction-in-pydagnodesutilsmailactionpy) |  | ![MailAction](element_icons/MailAction.png)
| [`MailBufferAction`](#mailbufferaction-in-pydagnodesutilsmailbufferactionpy) | An `Action` that send emails based on data from parent `Buffer`.This action expects the parent buffer to provide exactly three input keys(in this fixed order): `recipients`, `subject`, and `body`.Behavior:    - `recipients` may be a single email address (string) or a comma-separated        string / list of addresses accepted by the underlying SMTP `sendmail` call.    - `subject` and `body` are used to populate the message's Subject header        and HTML body respectively.    - The action connects to `smtp_server`:`port` and optionally starts TLS        (when `tls` is True). If `pw` is provided the action will attempt to        authenticate using `mail_account`/`pw`.    - When `debug_mode` is True, messages are not sent but logged for        inspection.Raises:        NodeException: if input keys are missing/invalid or if sending fails. | ![MailBufferAction](element_icons/MailBufferAction.png)
| [`OSKillProcessAction`](#oskillprocessaction-in-pydagnodesutilsoskillprocessactionpy) | `Node` that kills a specified OS process by its executable name.     | ![OSKillProcessAction](element_icons/OSKillProcessAction.png)
| [`OSProcessAction`](#osprocessaction-in-pydagnodesutilsosprocessactionpy) |  | ![OSProcessAction](element_icons/OSProcessAction.png)
| [`PrintAction`](#printaction-in-pydagnodesutilsprintactionpy) | An action that prints a message when executed. | ![PrintAction](element_icons/PrintAction.png)
| [`PrintBufferAction`](#printbufferaction-in-pydagnodesutilsprintbufferactionpy) | utility `Action` to print the parents' resultsArgs:    BufferNode (_type_): _description_    Action (_type_): _description_ | ![PrintBufferAction](element_icons/PrintBufferAction.png)
| [`SleepAction`](#sleepaction-in-pydagnodesutilssleepactionpy) | An action that sleeps for a specified number of seconds. | ![SleepAction](element_icons/SleepAction.png)
| [`SleepUntilAction`](#sleepuntilaction-in-pydagnodesutilssleepuntilactionpy) | An action that sleeps until the specified daytime. | ![SleepUntilAction](element_icons/SleepUntilAction.png)
| [`StartAction`](#startaction-in-pydagnodesutilsstartactionpy) | An action that starts the state machine. | ![StartAction](element_icons/StartAction.png)
| [`StopAction`](#stopaction-in-pydagnodesutilsstopactionpy) | An action that stops the state machine. | ![StopAction](element_icons/StopAction.png)
| [`TrueTransition`](#truetransition-in-pydagnodesutilstruetransitionpy) | A transition that always returns True.This is used to test the statemachine without any conditions. | ![TrueTransition](element_icons/TrueTransition.png)
| [`OCRAction`](#ocraction-in-pydagnodesvisionocractionpy) | `Action` to perform OCR on images or pdfs that loaded from filepaths of parent `BufferNode`s and stored as extracted text in its `Buffer`.the action outputs extracted text and the source path with the keys ["path", "text"]Requirements:- make sure poopler is installed and on PATH (in windows)https://github.com/oschwartz10612/poppler-windows/releases/tag/v25.11.0-0- make sure tesseract is installed and on PATH (in windows)https://tesseract-ocr.github.io/tessdoc/Installation.html and https://github.com/UB-Mannheim/tesseract/wiki (for windows) | ![OCRAction](element_icons/OCRAction.png)
| [`BrowserAutomationAction`](#browserautomationaction-in-pydagnodeswebbrowserbrowserautomationactionpy) |  | ![BrowserAutomationAction](element_icons/BrowserAutomationAction.png)
| [`BrowserClickElementAction`](#browserclickelementaction-in-pydagnodeswebbrowserbrowserclickelementactionpy) |  | ![BrowserClickElementAction](element_icons/BrowserClickElementAction.png)
| [`BrowserGetElementAction`](#browsergetelementaction-in-pydagnodeswebbrowserbrowsergetelementactionpy) |  | ![BrowserGetElementAction](element_icons/BrowserGetElementAction.png)
| [`BrowserSetElementAction`](#browsersetelementaction-in-pydagnodeswebbrowserbrowsersetelementactionpy) |  | ![BrowserSetElementAction](element_icons/BrowserSetElementAction.png)
| [`BrowserUrlNavigateAction`](#browserurlnavigateaction-in-pydagnodeswebbrowserbrowserurlnavigateactionpy) | `Action` for navigating a Browser Automation Object to a new urlRaises:    NodeException: if referenced `self._service`  is not of type `BrowserAutomationService` | ![BrowserUrlNavigateAction](element_icons/BrowserUrlNavigateAction.png)



## `Action` (in `pydag\nodes\Action.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `Action`
from pydag.nodes.Action import Action  # Adjust import if needed

obj = Action()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `AgentNode` (in `pydag\nodes\AgentNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `AgentNode`
from pydag.nodes.AgentNode import AgentNode  # Adjust import if needed

obj = AgentNode()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `BufferNode` (in `pydag\nodes\BufferNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |


```python
# Example usage of `BufferNode`
from pydag.nodes.BufferNode import BufferNode  # Adjust import if needed

obj = BufferNode()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
```

[Go to Summary](#summary)
## `LearningNode` (in `pydag\nodes\LearningNode.py`)

LearningNode is a base class for elements that require a learning step in their pipeline execution.
It extends the BufferNode class and provides additional functionality specific to learning tasks.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |


```python
# Example usage of `LearningNode`
from pydag.nodes.LearningNode import LearningNode  # Adjust import if needed

obj = LearningNode()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
```

[Go to Summary](#summary)
## `Node` (in `pydag\nodes\Node.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |


```python
# Example usage of `Node`
from pydag.nodes.Node import Node  # Adjust import if needed

obj = Node()
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.child_ids='list()'
```

[Go to Summary](#summary)
## `ServiceNode` (in `pydag\nodes\ServiceNode.py`)

A class representing a service node in a state machine.
Inherits from Node and adds functionality specific to service nodes.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `service_id` | `str` | `` | ID of the service |


```python
# Example usage of `ServiceNode`
from pydag.nodes.ServiceNode import ServiceNode  # Adjust import if needed

obj = ServiceNode()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.service_id="<string>"
```

[Go to Summary](#summary)
## `Transition` (in `pydag\nodes\Transition.py`)

A `Transition` `Node` that defines conditions for state transitions in a state machine.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `Transition`
from pydag.nodes.Transition import Transition  # Adjust import if needed

obj = Transition()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `TriggerAction` (in `pydag\nodes\TriggerAction.py`)

Abstract `Action` `Node`that defines the interface for `Node`s with trigger logic, that are not executed directly within a `StatemachineService`,
but are rather started from external events and trigger the execution `StatemachineService`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `TriggerAction`
from pydag.nodes.TriggerAction import TriggerAction  # Adjust import if needed

obj = TriggerAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `AddBufferAction` (in `pydag\nodes\buffers\AddBufferAction.py`)

Action to add a buffer to the agent node.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `config` | `dict` | `` | Configuration for the buffer to be added. |


```python
# Example usage of `AddBufferAction`
from pydag.nodes.buffers.AddBufferAction import AddBufferAction  # Adjust import if needed

obj = AddBufferAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.config={}
```

[Go to Summary](#summary)
## `BufferEmptyTransition` (in `pydag\nodes\buffers\BufferEmptyTransition.py`)

A transition that checks if specified buffer is empty.
If the buffer is empty, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `BufferEmptyTransition`
from pydag.nodes.buffers.BufferEmptyTransition import BufferEmptyTransition  # Adjust import if needed

obj = BufferEmptyTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `BufferExtractAction` (in `pydag\nodes\buffers\BufferExtractAction.py`)

`Action` for extracting data from a specified buffer and to store the extracted data into this buffer.
This `Action` can only be applied on if the specified buffer is of type `DictBuffer`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `extract_buffer_id` | `str` | `` | id of the buffer to extract data from |


```python
# Example usage of `BufferExtractAction`
from pydag.nodes.buffers.BufferExtractAction import BufferExtractAction  # Adjust import if needed

obj = BufferExtractAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.extract_buffer_id="<string>"
```

[Go to Summary](#summary)
## `BufferInRangeTransition` (in `pydag\nodes\buffers\BufferInRangeTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `comparator` | `str` | `` | the comparison operator to use |
| `upper_limit` | `any` | `` | the upper limit of the range |
| `lower_limit` | `any` | `` | the lower limit of the range |


```python
# Example usage of `BufferInRangeTransition`
from pydag.nodes.buffers.BufferInRangeTransition import BufferInRangeTransition  # Adjust import if needed

obj = BufferInRangeTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.comparator="<string>"
obj.upper_limit="<value>"
obj.lower_limit="<value>"
```

[Go to Summary](#summary)
## `BufferNotEmptyTransition` (in `pydag\nodes\buffers\BufferNotEmptyTransition.py`)

A transition that checks if specified buffer is not empty.
If the buffer is not empty, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `BufferNotEmptyTransition`
from pydag.nodes.buffers.BufferNotEmptyTransition import BufferNotEmptyTransition  # Adjust import if needed

obj = BufferNotEmptyTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ClearBufferAction` (in `pydag\nodes\buffers\ClearBufferAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `ClearBufferAction`
from pydag.nodes.buffers.ClearBufferAction import ClearBufferAction  # Adjust import if needed

obj = ClearBufferAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CompareBufferTransition` (in `pydag\nodes\buffers\CompareBufferTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `CompareBufferTransition`
from pydag.nodes.buffers.CompareBufferTransition import CompareBufferTransition  # Adjust import if needed

obj = CompareBufferTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.comparator="<string>"
obj.value="<value>"
```

[Go to Summary](#summary)
## `CopyBufferAction` (in `pydag\nodes\buffers\CopyBufferAction.py`)

`Action` that copies the entire parent buffer to this `Node`'s `Buffer` whenever executed.
The copy procedure makes a deep of all the parent's `Buffer` elements
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `CopyBufferAction`
from pydag.nodes.buffers.CopyBufferAction import CopyBufferAction  # Adjust import if needed

obj = CopyBufferAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CopyDataAction` (in `pydag\nodes\buffers\CopyDataAction.py`)

`Action` that makes a copy of the data in all parent `Buffer`s found amongst this `Node`s parents.
If this `Node`'s parents contains more than one `BufferNode`, all data is merged and copied.
Before this `Node`s `Buffer` is filled, all other elements are cleared.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `clear_first` | `bool` | `True` | if set to true, this Buffer's content is cleared before copying |


```python
# Example usage of `CopyDataAction`
from pydag.nodes.buffers.CopyDataAction import CopyDataAction  # Adjust import if needed

obj = CopyDataAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.clear_first=True
```

[Go to Summary](#summary)
## `DataFrameFilterAction` (in `pydag\nodes\buffers\DataFrameFilterAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `row_filter` | `str` | `` | pandas filter command to apply to filter the rows of the buffer converted to dataframe |
| `column_filter` | `list[str]` | `'list()'` | list of columns to filter for |


```python
# Example usage of `DataFrameFilterAction`
from pydag.nodes.buffers.DataFrameFilterAction import DataFrameFilterAction  # Adjust import if needed

obj = DataFrameFilterAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.row_filter="<string>"
obj.column_filter='list()'
```

[Go to Summary](#summary)
## `DataToBuffersAction` (in `pydag\nodes\buffers\DataToBuffersAction.py`)

`Action` that copies data of the `Buffer` specified via `buffer_id` or found in the first `BufferNode` found amongst this `Node`s parents to all the buffers specified via `buffer_ids`.
If this `Node`'s parents contain more than one `BufferNode`, only the first is respected.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `clear_first` | `bool` | `True` | if set to true, this Buffer's content is cleared before copying |
| `buffer_ids` | `list[str]` | `'list()'` | ids of the buffers to copy data to |


```python
# Example usage of `DataToBuffersAction`
from pydag.nodes.buffers.DataToBuffersAction import DataToBuffersAction  # Adjust import if needed

obj = DataToBuffersAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.clear_first=True
obj.buffer_ids='list()'
```

[Go to Summary](#summary)
## `FormatBufferColumnAction` (in `pydag\nodes\buffers\FormatBufferColumnAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `create_new` | `bool` | `True` | specifies whether to create a new Buffer or append the referenced one |
| `format_keys` | `list[str]` | `'list[str]()'` | specifies the keys to use from original buffer(s) to format new column |
| `new_key` | `str` | `` | specifies the new column key for the formatted data |
| `format_pattern` | `str` | `` | specifies the format pattern for the new column |


```python
# Example usage of `FormatBufferColumnAction`
from pydag.nodes.buffers.FormatBufferColumnAction import FormatBufferColumnAction  # Adjust import if needed

obj = FormatBufferColumnAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.create_new=True
obj.format_keys='list[str]()'
obj.new_key="<string>"
obj.format_pattern="<string>"
```

[Go to Summary](#summary)
## `FormattedStringAction` (in `pydag\nodes\buffers\FormattedStringAction.py`)

`Action` to compose a formatted string and store it in this `Action`'s buffer
using its parent's buffer to create the new string
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `template` | `str` | `` | string template to insert the data from the parent buffer into, e.g. 'Hi {}, are you from {}' |


```python
# Example usage of `FormattedStringAction`
from pydag.nodes.buffers.FormattedStringAction import FormattedStringAction  # Adjust import if needed

obj = FormattedStringAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.template="<string>"
```

[Go to Summary](#summary)
## `LinkBufferAction` (in `pydag\nodes\buffers\LinkBufferAction.py`)

`Action` that's only function is to link a buffer from agent to the statemachine
therefore an empty execute method is provided
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `LinkBufferAction`
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction  # Adjust import if needed

obj = LinkBufferAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `SampledSignalAction` (in `pydag\nodes\buffers\SampledSignalAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `signal` | `SampledSignal` | `` |  |


```python
# Example usage of `SampledSignalAction`
from pydag.nodes.buffers.SampledSignalAction import SampledSignalAction  # Adjust import if needed

obj = SampledSignalAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.signal="<value>"
```

[Go to Summary](#summary)
## `ShiftMonitoring` (in `pydag\nodes\clustering\ShiftMonitoring.py`)

ShiftMonitoring is a LearningNode that monitors distributional shifts in incoming data. It uses statistical methods to compare the distribution of new data against learned distributions and can identify when a significant shift occurs.
Returns the deviation as well as the outlier-decision to the first distribution "A", even if n_distributions > 2.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `inference_buffer_size` | `int` | `10000000.0` | Size of the buffer for the inference data. This is the data which is appended to the training data to calculate the distribution to compare with the distribution of the training data. |
| `bin_count` | `int` | `10` | number of bins per dimension of the grid. Each dimension is spanned by one value of the input data, e.g. if you have data like [[10,2,2],....,[12,2,5]], the first dimension is spanned by the values [10, ..., 12 ] and so on. Can be imagined as the # of squares in x and y direction. The features are binned to the number of bins to calculate the distribution. |
| `compare_mode` | `str` | `'CompareMode.JSD.value'` | The comparison function which is used to compare the distribution of the training data with the distribution of the inference data. |
| `n_distributions` | `int` | `2` | The number of distributions which can be calculated from the data. If set to 2, all points which deviate from A are put to A'. This is similar to distribution shift monitoring from an initial base distribution, like e.g. an Process in OK-State or the like. If set to n, points which deviate from A .... A^(n-1) are put to A^n. n > 2 is not implemented yet. |
| `return_input` | `bool` | `False` | if True the input data is returned in the output dictionary as well |
| `sensitivity` | `float` | `1.0` | Sensitivity factor for threshold calculation in units of standard deviations. Higher values make the detection less sensitive. |
| `shift_name` | `str` | `'shift'` | The name of the shift feature in the output dictionary. |
| `decision_name` | `str` | `'decision'` | The name of the decision feature in the output dictionary. |


```python
# Example usage of `ShiftMonitoring`
from pydag.nodes.clustering.ShiftMonitoring import ShiftMonitoring  # Adjust import if needed

obj = ShiftMonitoring()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.inference_buffer_size=10000000.0
obj.bin_count=10
obj.compare_mode='CompareMode.JSD.value'
obj.n_distributions=2
obj.return_input=False
obj.sensitivity=1.0
obj.shift_name='shift'
obj.decision_name='decision'
```

[Go to Summary](#summary)
## `PivotAction` (in `pydag\nodes\db\PivotAction.py`)

Args:
    BufferNode (_type_): _description_
    Action (_type_): _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `index` | `str | list` | `'list()'` |  |
| `columns` | `str | list` | `'list()'` |  |
| `values` | `str | list` | `'list()'` |  |
| `aggfunc` | `str | list` | `'list()'` |  |


```python
# Example usage of `PivotAction`
from pydag.nodes.db.PivotAction import PivotAction  # Adjust import if needed

obj = PivotAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.index='list()'
obj.columns='list()'
obj.values='list()'
obj.aggfunc='list()'
```

[Go to Summary](#summary)
## `SQLAction` (in `pydag\nodes\db\SQLAction.py`)

`Action` node to perform SQL operations using the pyodbc library.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `connection_str` | `str` | `` | connection string for the specific SQL database |
| `query` | `str` | `` | SQL query to execute. If `input_keys` are defined, the query is treated as a parameterized query and values are taken from the buffers. |


```python
# Example usage of `SQLAction`
from pydag.nodes.db.SQLAction import SQLAction  # Adjust import if needed

obj = SQLAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.connection_str="<string>"
obj.query="<string>"
```

[Go to Summary](#summary)
## `IsomapDimReduction` (in `pydag\nodes\dimreduction\IsomapDimReduction.py`)

Dimensionality reduction using Isomap algorithm. Mind, that the Algorithms is trained on two dimensional data with shape (n_samples, n_features). 
Hence sample_length should be larger than the number of dimensions. 
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `dimensions` | `int` | `2` | number of dimensions to reduce the data to |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `IsomapDimReduction`
from pydag.nodes.dimreduction.IsomapDimReduction import IsomapDimReduction  # Adjust import if needed

obj = IsomapDimReduction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.dimensions=2
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `LocallyLinearEmbeddingsReduction` (in `pydag\nodes\dimreduction\LocallyLinearEmbeddingsReduction.py`)

Dimensionality reduction using LocallyLinearEmbeddings algorithm. Mind, that the Algorithms is trained on two dimensional data with shape (n_samples, n_features). 
Hence sample_length should be larger than the number of dimensions. 
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `dimensions` | `int` | `2` |  |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `LocallyLinearEmbeddingsReduction`
from pydag.nodes.dimreduction.LocallyLinearEmbeddingsReduction import LocallyLinearEmbeddingsReduction  # Adjust import if needed

obj = LocallyLinearEmbeddingsReduction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.dimensions=2
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `PCADimReduction` (in `pydag\nodes\dimreduction\PCADimReduction.py`)

Dimensionality reduction using PCA algorithm. Mind, that the Algorithms is trained on two dimensional data with shape (n_samples, n_features). 
Hence sample_length should be larger than the number of dimensions. 
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `dimensions` | `int` | `2` |  |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `PCADimReduction`
from pydag.nodes.dimreduction.PCADimReduction import PCADimReduction  # Adjust import if needed

obj = PCADimReduction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.dimensions=2
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `CompressAction` (in `pydag\nodes\documents\CompressAction.py`)

`Action` that converts the specified `source_file` to compressed archive file under the new filepath `target_file`    
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `source_file` | `str` | `` | path of the source file for being compressed. If source_file is a folder, the whole folder will be compressed. |
| `target_file` | `str` | `` | new target filepath. If a folder is specified, the name of the source file is used. If no target filepath is specified, the file is compressed in place. |


```python
# Example usage of `CompressAction`
from pydag.nodes.documents.CompressAction import CompressAction  # Adjust import if needed

obj = CompressAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.source_file="path/to/file.txt"
obj.target_file="path/to/file.txt"
```

[Go to Summary](#summary)
## `ConvertFile2Base64Action` (in `pydag\nodes\documents\ConvertFile2Base64Action.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `file_paths` | `list[str]` | `'list()'` | path to the file to convert to base64, e.g. PNG | JPG | PDF | MP4 | AVI | MOV | MP3 |


```python
# Example usage of `ConvertFile2Base64Action`
from pydag.nodes.documents.ConvertFile2Base64Action import ConvertFile2Base64Action  # Adjust import if needed

obj = ConvertFile2Base64Action()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.file_paths='list()'
```

[Go to Summary](#summary)
## `CopyFilesAction` (in `pydag\nodes\documents\CopyFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to copy all the files to in Buffer |


```python
# Example usage of `CopyFilesAction`
from pydag.nodes.documents.CopyFilesAction import CopyFilesAction  # Adjust import if needed

obj = CopyFilesAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

[Go to Summary](#summary)
## `DecompressAction` (in `pydag\nodes\documents\DecompressAction.py`)

`Action` that decompresses the specified `source_file` under the new filepath `target_dir`    
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `source_file` | `str` | `` | path of the source file for being compressed. If source_file is a folder, the whole folder will be compressed. |
| `target_dir` | `str` | `` | new target filepath. If a folder is specified, the name of the source file is used. If no target filepath is specified, the file is compressed in place. |


```python
# Example usage of `DecompressAction`
from pydag.nodes.documents.DecompressAction import DecompressAction  # Adjust import if needed

obj = DecompressAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.source_file="path/to/file.txt"
obj.target_dir="<string>"
```

[Go to Summary](#summary)
## `DocxTemplateAction` (in `pydag\nodes\documents\DocxTemplateAction.py`)

`Action` for writing data to DOCX template document.

buffers of parent elements can be used to populate the docx file, if `buffer_id` or `set_buffer(...)` is specified then only this buffer is used
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `output_path` | `str` | `'output.docx'` | output path for the template to be saved to |
| `template_path` | `str` | `` | template file path |


```python
# Example usage of `DocxTemplateAction`
from pydag.nodes.documents.DocxTemplateAction import DocxTemplateAction  # Adjust import if needed

obj = DocxTemplateAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.output_path='output.docx'
obj.template_path="<string>"
```

[Go to Summary](#summary)
## `HTMLFileAction` (in `pydag\nodes\documents\HTMLFileAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `path` | `str` | `` | output folder or filepath to write the HTML files to, if a file is specified, then all html strings retrieved are (over)written to this location, if a folder is specified, then all html strings are written to files in this folder with the name schema <key>_<COUNTER>.html |
| `encoding` | `str` | `'utf-8'` | encoding for html file(s), defalts to utf-8 |
| `output_keys` | `list[str]` | `"lambda: ['path']()"` | default output_keys are 'path', for this node only ever one output key is required |


```python
# Example usage of `HTMLFileAction`
from pydag.nodes.documents.HTMLFileAction import HTMLFileAction  # Adjust import if needed

obj = HTMLFileAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.path="<string>"
obj.encoding='utf-8'
obj.output_keys="lambda: ['path']()"
```

[Go to Summary](#summary)
## `HTMLTableAction` (in `pydag\nodes\documents\HTMLTableAction.py`)

This `BufferNode` creates a HTML Table string based on the parent data input to this `Node`.
By default it outputs the HTML to a key named 'html' for child `Node`s to consume.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `output_keys` | `list[str]` | `"lambda: ['html']()"` |  |


```python
# Example usage of `HTMLTableAction`
from pydag.nodes.documents.HTMLTableAction import HTMLTableAction  # Adjust import if needed

obj = HTMLTableAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.output_keys="lambda: ['html']()"
```

[Go to Summary](#summary)
## `ICalAction` (in `pydag\nodes\documents\ICalAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `ical_path` | `str` | `` | path for ics file export, full path to the file |
| `date_format` | `str` | `'%d.%m.%Y'` | date format to parse the incoming date fields from |
| `name_key` | `str` | `` | name of the key that contains the event name |
| `start_key` | `str` | `` | name of the key that contains the start date |
| `end_key` | `str` | `` | name of the key that contains the end date |
| `description_key` | `str` | `` | name of the key that contains the event description |
| `location_key` | `str` | `` | name of the key that contains the location of the event |
| `time_zone` | `str` | `'Europe/Berlin'` | name of the key that contains the time zone info |


```python
# Example usage of `ICalAction`
from pydag.nodes.documents.ICalAction import ICalAction  # Adjust import if needed

obj = ICalAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.ical_path="<string>"
obj.date_format='%d.%m.%Y'
obj.name_key="John Doe"
obj.start_key="<string>"
obj.end_key="<string>"
obj.description_key="<string>"
obj.location_key="<string>"
obj.time_zone='Europe/Berlin'
```

[Go to Summary](#summary)
## `ListFilesAction` (in `pydag\nodes\documents\ListFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `folder` | `str` | `` | folder to list the files from into a Buffer |
| `pattern` | `Union[str | list[str]]` | `` | pattern to look for in file names, can be str or list, e.g. ['png', 'jpg'] |
| `extension` | `str` | `` | extension to include |
| `newer_than_seconds` | `int` | `` | specifies how old in seconds a file can be to be included |
| `recursive` | `bool` | `False` | specifies whether to search subdirectories aswell |


```python
# Example usage of `ListFilesAction`
from pydag.nodes.documents.ListFilesAction import ListFilesAction  # Adjust import if needed

obj = ListFilesAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.folder="path/to/folder"
obj.pattern="<string>"
obj.extension="<string>"
obj.newer_than_seconds=1
obj.recursive=False
```

[Go to Summary](#summary)
## `MoveFilesAction` (in `pydag\nodes\documents\MoveFilesAction.py`)

`Action` that moves files to a new `target_folder`
<br>this `Action` either needs a parent `Node` with a `ListBuffer` with filepaths or a reference to a `Buffer` via `buffer_id` or its `buffer`variable

Raises:
    StatemachineException: if folder does not exist or wrong `Buffer` is provided
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to move all the files to in Buffer |


```python
# Example usage of `MoveFilesAction`
from pydag.nodes.documents.MoveFilesAction import MoveFilesAction  # Adjust import if needed

obj = MoveFilesAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

[Go to Summary](#summary)
## `PDFReadFormAction` (in `pydag\nodes\documents\PDFReadFormAction.py`)

Extract context-rich AcroForm fields from PDF files using PyMuPDF.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `input_keys` | `list[str]` | `"lambda: ['values']()"` | parent buffer keys to scan for PDF file paths |
| `output_keys` | `list[str]` | `"lambda: ['filepath', 'metadata', 'fields', 'full_text_content', 'llm_prompt']()"` | output columns for source path, metadata, extracted fields, page text, and the llm_prompt bridge column used by downstream form-filling LLM steps; exactly 5 output_keys are mandatory, and llm_prompt must remain present even when include_bridge_prompt=False (it is then emitted as an empty string) |
| `row_mode` | `str` | `'per_pdf'` | row shape of emitted data: per_pdf emits one row per file, per_field emits one row per field |
| `include_bridge_prompt` | `bool` | `True` | whether to generate and emit an llm_prompt bridge string for each output row |
| `emit_writable_only` | `bool` | `True` | whether to keep only writable form fields and skip read-only or unsupported widgets |
| `require_pdf_extension` | `bool` | `True` | whether file paths must end with .pdf |
| `label_search_left` | `float` | `90.0` | horizontal label-search range in points to the left of each field rectangle |
| `label_search_above` | `float` | `60.0` | vertical label-search range in points above each field rectangle |
| `label_search_right` | `float` | `20.0` | horizontal label-search range in points to the right of each field rectangle |
| `context_search_padding` | `float` | `140.0` | padding in points around a field rectangle for selecting nearby page context text |


```python
# Example usage of `PDFReadFormAction`
from pydag.nodes.documents.PDFReadFormAction import PDFReadFormAction  # Adjust import if needed

obj = PDFReadFormAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.input_keys="lambda: ['values']()"
obj.output_keys="lambda: ['filepath', 'metadata', 'fields', 'full_text_content', 'llm_prompt']()"
obj.row_mode='per_pdf'
obj.include_bridge_prompt=True
obj.emit_writable_only=True
obj.require_pdf_extension=True
obj.label_search_left=90.0
obj.label_search_above=60.0
obj.label_search_right=20.0
obj.context_search_padding=140.0
```

[Go to Summary](#summary)
## `PDFWriteFormAction` (in `pydag\nodes\documents\PDFWriteFormAction.py`)

Write LLM- or user-provided values into PDF AcroForm fields using PyMuPDF.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `path_input_keys` | `list[str]` | `"lambda: ['values', 'filepath', 'pdf_path']()"` | parent buffer keys to scan for source PDF file paths |
| `fill_input_keys` | `list[str]` | `"lambda: ['answer', 'answers', 'fields', 'field_values', 'llm_data', 'content']()"` | parent buffer keys to scan for strict field_updates payloads whose field values are the final PDF write instructions: each update uses internal_field_id plus either value for text/dropdown/list fields or selected_state for checkbox/radio fields |
| `row_mode` | `str` | `'per_pdf'` | payload interpretation mode: per_pdf expects one payload per file, per_field can merge field-level rows |
| `output_keys` | `list[str]` | `"lambda: ['filepath', 'output_filepath', 'written_fields', 'written_field_count']()"` | output columns for source path, written file path, field map, and number of written fields |
| `output_folder` | `str | None` | `'resources/outputs'` | target folder for written PDFs; ignored when overwrite_source is True |
| `output_suffix` | `str` | `'_filled'` | suffix appended to the source filename stem for generated output files |
| `overwrite_source` | `bool` | `False` | whether to overwrite the source PDF in place instead of writing a separate output file |
| `flatten` | `bool` | `False` | whether to flatten form fields after writing values |
| `strict_unknown_fields` | `bool` | `True` | whether to raise an error if payload contains field names that are not present in the PDF |
| `require_pdf_extension` | `bool` | `True` | whether file paths must end with .pdf |


```python
# Example usage of `PDFWriteFormAction`
from pydag.nodes.documents.PDFWriteFormAction import PDFWriteFormAction  # Adjust import if needed

obj = PDFWriteFormAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.path_input_keys="lambda: ['values', 'filepath', 'pdf_path']()"
obj.fill_input_keys="lambda: ['answer', 'answers', 'fields', 'field_values', 'llm_data', 'content']()"
obj.row_mode='per_pdf'
obj.output_keys="lambda: ['filepath', 'output_filepath', 'written_fields', 'written_field_count']()"
obj.output_folder='resources/outputs'
obj.output_suffix='_filled'
obj.overwrite_source=False
obj.flatten=False
obj.strict_unknown_fields=True
obj.require_pdf_extension=True
```

[Go to Summary](#summary)
## `PlotlifyAction` (in `pydag\nodes\documents\PlotlifyAction.py`)

`Action` that generates a plotly file based on the data and layout specified and extracted from the specified buffer or its parents `Buffer`s.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `plot_path` | `str` | `` | path for plotly html file |
| `data` | `list[dict]` | `'list[dict]()'` | plotly data dictionary with buffer keys for x,y,z data |
| `layout` | `dict` | `'dict()'` | plotly layout dictionary |
| `open_in_browser` | `bool` | `True` | specifies whether to open the plotly file in browser after creation |
| `auto_refresh` | `int` | `0` | if an interval greater than 0s is specified, then an meta-tag for page auto refresh is added to html |
| `colors` | `list[str]` | `` | lets you specify the colors to use from, when creating traces |


```python
# Example usage of `PlotlifyAction`
from pydag.nodes.documents.PlotlifyAction import PlotlifyAction  # Adjust import if needed

obj = PlotlifyAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.plot_path="<string>"
obj.data='list[dict]()'
obj.layout='dict()'
obj.open_in_browser=True
obj.auto_refresh=0
obj.colors="<string>"
```

[Go to Summary](#summary)
## `ReadCsvAction` (in `pydag\nodes\documents\ReadCsvAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the csv file to read the data from |
| `delimiter` | `str` | `';'` | delimiter character(s) for this csv file |


```python
# Example usage of `ReadCsvAction`
from pydag.nodes.documents.ReadCsvAction import ReadCsvAction  # Adjust import if needed

obj = ReadCsvAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.delimiter=';'
```

[Go to Summary](#summary)
## `ReadExcelRangeAction` (in `pydag\nodes\documents\ReadExcelRangeAction.py`)

This `Action` reads data from specified workbook, worksheet and range

Args:
    BufferNode (_type_): _description_
    Action (_type_): _description_

Raises:
    NodeException: _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | path to the excel files to read the range from |
| `worksheet` | `Union[str | int]` | `` | name of the worksheet inside the excel to read from or the index of the worksheet starting with 0 for the first worksheet |
| `range` | `str` | `` | address of the range in the worksheet inside the excel to read from |
| `has_header` | `bool` | `False` | specifies whether the first row in range contains header descriptions |


```python
# Example usage of `ReadExcelRangeAction`
from pydag.nodes.documents.ReadExcelRangeAction import ReadExcelRangeAction  # Adjust import if needed

obj = ReadExcelRangeAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
obj.worksheet="<string>"
obj.range="<string>"
obj.has_header=False
```

[Go to Summary](#summary)
## `ReadExcelTableAction` (in `pydag\nodes\documents\ReadExcelTableAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | path to the excel files to read named table from |
| `table_name` | `str` | `` | name of the table inside the excel to read from |


```python
# Example usage of `ReadExcelTableAction`
from pydag.nodes.documents.ReadExcelTableAction import ReadExcelTableAction  # Adjust import if needed

obj = ReadExcelTableAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
obj.table_name="John Doe"
```

[Go to Summary](#summary)
## `ReadExcelWorksheetAction` (in `pydag\nodes\documents\ReadExcelWorksheetAction.py`)

This `BufferNode` reads the entire content of a specified Excel worksheet into a buffer.

It automatically detects the first worksheet with data if no specific worksheet is specified,
finds the connected range of data, and uses the first row as headers by default.

Args:
    BufferNode: Provides buffer management functionality
    Action: Provides action execution framework
    
Raises:
    NodeException: If file not found, worksheet not found, or no data found in worksheet
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | Path to the Excel file to read from |
| `worksheet` | `Union[str, int]` | `` | Name (str) or index (int, 0-based) of the worksheet. If None, reads from first worksheet with data |
| `start_range` | `str` | `` | Cell address to start reading from (e.g., 'A1'). If None, auto-detects the first connected data range |
| `has_header` | `bool` | `True` | If True, treats first row as column headers. If False, generates COL0, COL1, etc. |


```python
# Example usage of `ReadExcelWorksheetAction`
from pydag.nodes.documents.ReadExcelWorksheetAction import ReadExcelWorksheetAction  # Adjust import if needed

obj = ReadExcelWorksheetAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
obj.worksheet="<string>"
obj.start_range="<string>"
obj.has_header=True
```

[Go to Summary](#summary)
## `ReadJsonAction` (in `pydag\nodes\documents\ReadJsonAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the json file to read the data from |
| `json_path` | `str` | `` | json schema to parse the file for |
| `encoding` | `str` | `'utf-8'` | name of the file encoding to use, e.g. utf-8 (default), utf-16, ... |


```python
# Example usage of `ReadJsonAction`
from pydag.nodes.documents.ReadJsonAction import ReadJsonAction  # Adjust import if needed

obj = ReadJsonAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.json_path="<string>"
obj.encoding='utf-8'
```

[Go to Summary](#summary)
## `ReadNpzAction` (in `pydag\nodes\documents\ReadNpzAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the *.npz file to read the data from |


```python
# Example usage of `ReadNpzAction`
from pydag.nodes.documents.ReadNpzAction import ReadNpzAction  # Adjust import if needed

obj = ReadNpzAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.file_path="path/to/file.txt"
```

[Go to Summary](#summary)
## `ReadPDFFormAction` (in `pydag\nodes\documents\ReadPDFFormAction.py`)

`Action` that extracts AcroForm fields and text from PDFs.

Limitation:
This action only extracts native PDF AcroForm data. PDFs without AcroForm fields
return an empty `fields` list.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `input_keys` | `list[str]` | `"lambda: ['values']()"` | keys to read file paths from parent buffer data |
| `output_keys` | `list[str]` | `"lambda: ['filepath', 'metadata', 'fields', 'full_text_content']()"` | output keys in the order [filepath, metadata, fields, full_text_content] |
| `label_y_tolerance` | `float` | `18.0` | Maximum vertical distance (PDF points) between a form field and nearby text considered as label context. |
| `label_max_tokens` | `int` | `6` | Maximum number of words kept from inferred label context to avoid long/noisy labels. |
| `require_pdf_extension` | `bool` | `True` | If True, reject non-.pdf paths before parsing; if False, attempt parsing any file path with PdfReader. |


```python
# Example usage of `ReadPDFFormAction`
from pydag.nodes.documents.ReadPDFFormAction import ReadPDFFormAction  # Adjust import if needed

obj = ReadPDFFormAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.input_keys="lambda: ['values']()"
obj.output_keys="lambda: ['filepath', 'metadata', 'fields', 'full_text_content']()"
obj.label_y_tolerance=18.0
obj.label_max_tokens=6
obj.require_pdf_extension=True
```

[Go to Summary](#summary)
## `ReadXMLAction` (in `pydag\nodes\documents\ReadXMLAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the xml file to read the data from |
| `xpath` | `str` | `` | xml xpath schema to parse the file for |


```python
# Example usage of `ReadXMLAction`
from pydag.nodes.documents.ReadXMLAction import ReadXMLAction  # Adjust import if needed

obj = ReadXMLAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.xpath="<string>"
```

[Go to Summary](#summary)
## `WritePDFFormAction` (in `pydag\nodes\documents\WritePDFFormAction.py`)

`Action` that writes form values into parent-provided PDF files.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `path_input_keys` | `list[str]` | `"lambda: ['values', 'filepath']()"` | keys used to extract source PDF paths from parent data |
| `fill_input_keys` | `list[str]` | `"lambda: ['answer', 'answers', 'fields', 'form_fields', 'field_values', 'content']()"` | keys used to extract filled form payloads from parent data |
| `output_keys` | `list[str]` | `"lambda: ['filepath', 'output_filepath', 'written_fields', 'written_field_count']()"` | output keys in the order [filepath, output_filepath, written_fields, written_field_count] |
| `output_suffix` | `str` | `'_filled'` | suffix appended to output files when overwrite_source is False |
| `output_folder` | `str` | `` | optional folder for written PDFs; defaults to source file folder |
| `overwrite_source` | `bool` | `False` | if True, write directly into source PDFs |
| `require_pdf_extension` | `bool` | `True` | if True, reject non-.pdf inputs before parsing |
| `require_two_parents` | `bool` | `True` | if True, require at least two parents (paths + fill payloads) |


```python
# Example usage of `WritePDFFormAction`
from pydag.nodes.documents.WritePDFFormAction import WritePDFFormAction  # Adjust import if needed

obj = WritePDFFormAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.path_input_keys="lambda: ['values', 'filepath']()"
obj.fill_input_keys="lambda: ['answer', 'answers', 'fields', 'form_fields', 'field_values', 'content']()"
obj.output_keys="lambda: ['filepath', 'output_filepath', 'written_fields', 'written_field_count']()"
obj.output_suffix='_filled'
obj.output_folder="path/to/folder"
obj.overwrite_source=False
obj.require_pdf_extension=True
obj.require_two_parents=True
```

[Go to Summary](#summary)
## `CNN1DAutoencoder` (in `pydag\nodes\featureextraction\CNN1DAutoencoder.py`)

This `DataElement` represents a time series feature extraction model using a 1D CNN Autoencoder.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `input_length` | `int` | `5` |  |
| `input_features` | `int` | `1` |  |
| `epochs` | `int` | `10` |  |
| `batch_size` | `int` | `10` |  |
| `learning_rate` | `float` | `0.001` |  |
| `bottleneck_features` | `int` | `2` |  |
| `output_length` | `int` | `1` |  |
| `apply_per_feature` | `bool` | `True` |  |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |
| `y_hat_key` | `str` | `'AgentKeywords.Y_HAT'` | key to use for reconstructed output data of this Node. |


```python
# Example usage of `CNN1DAutoencoder`
from pydag.nodes.featureextraction.CNN1DAutoencoder import CNN1DAutoencoder  # Adjust import if needed

obj = CNN1DAutoencoder()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.input_length=5
obj.input_features=1
obj.epochs=10
obj.batch_size=10
obj.learning_rate=0.001
obj.bottleneck_features=2
obj.output_length=1
obj.apply_per_feature=True
obj.output_keys='list()'
obj.y_hat_key='AgentKeywords.Y_HAT'
```

[Go to Summary](#summary)
## `ChronosExtractor` (in `pydag\nodes\featureextraction\ChronosExtractor.py`)

Chronos Extractor for time series data. Returns 384-dimensional embeddings for each input time series sample using a pretrained Chronos model.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `model_name` | `str` | `'amazon/chronos-bolt-mini'` | name of available pretrained models, e.g. 'amazon/chronos-bolt-mini'. For further information look here: https://github.com/amazon-science/chronos-forecasting |
| `min_inference_samples` | `int` | `1` | Number of Samples to do inference on. |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `ChronosExtractor`
from pydag.nodes.featureextraction.ChronosExtractor import ChronosExtractor  # Adjust import if needed

obj = ChronosExtractor()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.model_name='amazon/chronos-bolt-mini'
obj.min_inference_samples=1
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `PSDExtractor` (in `pydag\nodes\featureextraction\PSDExtractor.py`)

PSD for time series data. Returns 261-dimensional embeddings for each input time series sample using the Welch method from https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html.
257 frequency bins + peak frequency + peak power + mean power + std power = 261 features per time series sample.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `min_inference_samples` | `int` | `1` | Number of Samples to do inference on. |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `PSDExtractor`
from pydag.nodes.featureextraction.PSDExtractor import PSDExtractor  # Adjust import if needed

obj = PSDExtractor()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.min_inference_samples=1
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `RIFEExtractor` (in `pydag\nodes\featureextraction\RIFEExtractor.py`)

Random Interval Feature Extractor for time series data.

Produces a 320 dimensional feature vector per input time series sample using
sktime's RandomIntervalFeatureExtractor with:
    - n_intervals = 64
    - features = [np.median, np.std, iqr, np.min, np.max]
yielding 64 * 5 = 320 features. Deterministic with random_state=42.

Notes:
    - No learning required (pure feature extraction).
    - Accepts input dictionary with one or multiple keys; each key's value must
      be a 1D array-like time series. Generates a single feature vector per key.
    - Output keys follow the pattern: "<orig_key>-feature-rife-<i>" where i is the
      index (0..255) of the feature.
    - The extractor samples random start–end pairs. Depending on the sktime version, intervals that are invalid (e.g. zero or 1-length after an internal constraint) can get skipped. In such cases, the output feature vector is zero-padded to 320 length.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `min_inference_samples` | `int` | `1` | Number of samples to accumulate before inference. |
| `sample_length` | `int` | `64` | Length of each input time series sample; must be >= MIN_SERIES_LENGTH for meaningful features. |
| `MIN_SERIES_LENGTH` | `int` | `` |  |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `RIFEExtractor`
from pydag.nodes.featureextraction.RIFEExtractor import RIFEExtractor  # Adjust import if needed

obj = RIFEExtractor()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.min_inference_samples=1
obj.sample_length=64
obj.MIN_SERIES_LENGTH=1
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `ROCKETExtractor` (in `pydag\nodes\featureextraction\ROCKETExtractor.py`)

ROCKET feature extractor.
https://www.sktime.net/en/stable/api_reference/auto_generated/sktime.transformations.panel.rocket.Rocket.html
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `num_of_kernels` | `int` | `10000` | Number of kernels used in the ROCKET model. |
| `min_learning_samples` | `int` | `1` | Number of Samples to learn on. Keep this, since ROCKET needs the sample only to instantiate the random kernels. Having more points does not improve performance. |
| `min_inference_samples` | `int` | `1` | Number of Samples to do inference on. |
| `normalize` | `bool` | `True` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `ROCKETExtractor`
from pydag.nodes.featureextraction.ROCKETExtractor import ROCKETExtractor  # Adjust import if needed

obj = ROCKETExtractor()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.sample_length=0
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.num_of_kernels=10000
obj.min_learning_samples=1
obj.min_inference_samples=1
obj.normalize=True
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `TirexExtractor` (in `pydag\nodes\featureextraction\TirexExtractor.py`)

This `DataElement` represents a time series feature extraction model using the TiREx framework.
Read: https://github.com/NX-AI/tirex
for more information.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `prediction_length` | `int` | `64` | length of the prediction horizon |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `TirexExtractor`
from pydag.nodes.featureextraction.TirexExtractor import TirexExtractor  # Adjust import if needed

obj = TirexExtractor()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.prediction_length=64
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `HttpGetAction` (in `pydag\nodes\http\HttpGetAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `url` | `str` | `` | url for HTTP GET method |
| `headers` | `dict[str]` | `` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `timeout` | `float` | `10` | timeout for requests |
| `json_path` | `str` | `` | JSONPath specififcation to parse or access the data in buffer |


```python
# Example usage of `HttpGetAction`
from pydag.nodes.http.HttpGetAction import HttpGetAction  # Adjust import if needed

obj = HttpGetAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.url="https://example.com"
obj.headers="<string>"
obj.timeout=10
obj.json_path="<string>"
```

[Go to Summary](#summary)
## `HttpPostAction` (in `pydag\nodes\http\HttpPostAction.py`)

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `url` | `str` | `` |  |
| `headers` | `dict[str]` | `` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `timeout` | `float` | `10` | timeout for requests |
| `json_path` | `str` | `` | JSONPath specififcation to parse the returned POST response |


```python
# Example usage of `HttpPostAction`
from pydag.nodes.http.HttpPostAction import HttpPostAction  # Adjust import if needed

obj = HttpPostAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.url="https://example.com"
obj.headers="<string>"
obj.timeout=10
obj.json_path="<string>"
```

[Go to Summary](#summary)
## `HttpPutAction` (in `pydag\nodes\http\HttpPutAction.py`)

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `url` | `str` | `` |  |
| `headers` | `dict[str]` | `` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `timeout` | `float` | `10` | timeout for requests |
| `json_path` | `str` | `` | JSONPath specififcation to parse the returned PUT response |


```python
# Example usage of `HttpPutAction`
from pydag.nodes.http.HttpPutAction import HttpPutAction  # Adjust import if needed

obj = HttpPutAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.url="https://example.com"
obj.headers="<string>"
obj.timeout=10
obj.json_path="<string>"
```

[Go to Summary](#summary)
## `HuggingFaceAction` (in `pydag\nodes\llm\HuggingFaceAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `task` | `str` | `` | task category of the model to use, e.g. image-classification, text-generation, sentiment-analysis, ... execute HuggingFaceNode.tasklist for full list |
| `model` | `str` | `` |  |
| `ignore_keys` | `list[str]` | `"lambda: ['index', 'timestamps']()"` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |


```python
# Example usage of `HuggingFaceAction`
from pydag.nodes.llm.HuggingFaceAction import HuggingFaceAction  # Adjust import if needed

obj = HuggingFaceAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.task="<string>"
obj.model="<string>"
obj.ignore_keys="lambda: ['index', 'timestamps']()"
```

[Go to Summary](#summary)
## `LLMChatAction` (in `pydag\nodes\llm\LLMChatAction.py`)

`Action` to chat with a `RAGService` and store the response in its `Buffer`.

Usage modes:
1. Chat-Only: (default) `RAGService` with `use_rag_context=False`, only `question`.
2. Chat-with-RAG-context: `RAGService` with `question`, retrieval enabled.
3. Chat-with-local-context: `RAGService` with `question` + `input_context`, `use_rag_context=False`.
4. Full-mode-augment: `question` + `input_context` + retrieval enabled, no strict structure enforcement.
5. Full-mode-template_fill: same as full augment plus strict structure validation.

Optional file context can be supplied via `context_files_key` or
`context_files_value`. V1 accepts external URLs, local file URLs, local
paths absolute or relative to the current working directory, data URIs, plain
base64 strings, raw bytes, or lists of those values. File inputs are supported
only for OPENAI and AZURE model providers. OLLAMA file processing is not
implemented yet; supplying files with OLLAMA emits a warning and continues
text-only.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `service_id` | `str` | `` | ID of the service |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `template` | `str` | `` | 
            Legacy question template fallback when question_key/question_value are not configured.
            For example: 'How much costs the article number {}?' or
            'Summarize the following text: {0}. And answer the following question: {1}'.
             |
| `question_key` | `str` | `` | Key from which to receive the data for the final task/question the model must answer. This is what the generated answer should respond to.  |
| `question_value` | `str` | `` | Fixed value for the final task/question the model must answer. This is what the generated answer should respond to. |
| `instruction_key` | `str` | `` | Key from which to receive prompt instructions. The resolved value is passed to RAGService.chat as instruction and rendered under the prompt's Instruction section; use it for answer rules, format, style, constraints, and priorities. |
| `instruction_value` | `str` | `` | Fixed prompt instructions for all rows. The value is passed to RAGService.chat as instruction and rendered under the prompt's Instruction section; use it for answer rules, format, style, constraints, and priorities. |
| `retrieval_query_key` | `str` | `` | Key from which to receive the The query used only for document retrieval from the vector store.  |
| `retrieval_query_value` | `str` | `` | Fixed value for the query used only for document retrieval from the vector store.  |
| `input_context_keys` | `list[str]` | `'list()'` | Key from which to receive the Additional runtime context passed directly from parent buffers (not retrieved from vector DB). |
| `input_context_value` | `str | dict | list | None` | `` | Fixed value for the Additional runtime context passed directly from parent buffers (not retrieved from vector DB). if input_context_keys is not configured, this value is used as the input context for all rows. |
| `context_files_key` | `str` | `` | Key from which to receive optional file context. V1 accepts str, bytes, or list[str | bytes]. |
| `context_files_value` | `str | bytes | list[str | bytes] | None` | `` | Fixed optional file context for all rows. V1 accepts external URLs, file URLs, local paths absolute or relative to the current working directory, data URIs, plain base64 strings, raw bytes, or lists of those values. |
| `input_context_mode` | `str` | `'augment'` | Either 'augment' or 'template_fill'. 'augment' mode simply appends the input_context to the question and feeds it to the model as one prompt. 'template_fill' mode treats the input_context as a template for the expected answer structure and enforces that the model's answer adheres to this structure by validating that all keys in the input_context are present in the model's answer and that there are no extra keys in the model's answer that are not present in the input_context. This is useful to ensure that the model's answer can be reliably parsed and processed downstream, but it also requires that the input_context is carefully crafted to match the expected answer format. |
| `use_rag_context` | `bool` | `False` | Set to False to disable vector retrieval for this action. |
| `pass_through_keys` | `list[str]` | `'list()'` | Row keys that should be copied unchanged to the output row. |
| `output_keys` | `list[str]` | `"lambda: ['question', 'answer']()"` |  |


```python
# Example usage of `LLMChatAction`
from pydag.nodes.llm.LLMChatAction import LLMChatAction  # Adjust import if needed

obj = LLMChatAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.service_id="<string>"
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.template="<string>"
obj.question_key="<string>"
obj.question_value="<string>"
obj.instruction_key="<string>"
obj.instruction_value="<string>"
obj.retrieval_query_key="<string>"
obj.retrieval_query_value="<string>"
obj.input_context_keys='list()'
obj.input_context_value="<string>"
obj.context_files_key="<string>"
obj.context_files_value="<string>"
obj.input_context_mode='augment'
obj.use_rag_context=False
obj.pass_through_keys='list()'
obj.output_keys="lambda: ['question', 'answer']()"
```

[Go to Summary](#summary)
## `LLMImageAnalysisAction` (in `pydag\nodes\llm\LLMImageAnalysisAction.py`)

`Action` to retrieve information from an image and store the response in its `Buffer`.
The Action analyses arbitrary images for its content (not only text documents like OCR). Hence it is powerful for image understanding tasks. 
If you specifically want to extract text as well as its formatting from images, consider using the LLMOCRAction instead.
The parent Buffer Node is expected to provide file paths to images or PDFs.
The allowed inpus formats for the file paths are:
- A fully qualified file path as a string
- an image as a Base64-encoded data URL 
- For OpanAI models: a file ID (created with the Files API (https://platform.openai.com/docs/api-reference/files))
The OpenAI API is used.
Keep in mind that the provided model must support image inputs, e.g. for OpenAI use "gpt-4o" or "gpt-4o-mini" or "gpt-4.1-mini" or "gpt-4.1" or "gpt-5".
For more models and providers refer to their documentation, e.g. OpenAI: https://platform.openai.com/docs/models".

The output has the following format:
{
    "question": <the question asked>,
    "answer": <the answer from the LLM>
    "filepath": <file path for each processed input>
}
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `template` | `str` | `` | Not in use for the LLMOCRAction, as the message format is fixed for image inputs. |
| `output_keys` | `list[str]` | `"lambda: ['question', 'answer', 'filepath']()"` |  |
| `question` | `str` | `' '` | The question to ask the LLM about the image content. |


```python
# Example usage of `LLMImageAnalysisAction`
from pydag.nodes.llm.LLMImageAnalysisAction import LLMImageAnalysisAction  # Adjust import if needed

obj = LLMImageAnalysisAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.template="<string>"
obj.output_keys="lambda: ['question', 'answer', 'filepath']()"
obj.question=' '
```

[Go to Summary](#summary)
## `LLMOCRAction` (in `pydag\nodes\llm\LLMOCRAction.py`)

`Action` to retrieve text from an image or PDF and store the extracted text in its `Buffer`.
The parent Buffer Node is expected to provide file paths to images or PDFs.
The allowed input formats for the file paths are:
- A fully qualified file path as a string
- an image as a Base64-encoded data URL 
The Mistral OCR-3 model is used to extract text from the images or PDFs.
For more information about the Mistral OCR-3 model: https://mistral.ai/news/mistral-ocr-3".

The output has the following format:
{
    "documents": <String of extracted text pages creatred from the contents of the origial OCRPageObject returned by Mistral>,
    "filepath": <file path for each processed input>
}
Where the original OCRPageObject has the following format:
    {
    "pages": [ # The content of each page
        {
        "index": int, # The index of the corresponding page
        "markdown": str, # The main output and raw markdown content
        "images": list, # Image information when images are extracted
        "tables": list, # Table information when using `table_format=html`
        "hyperlinks": list, # Hyperlinks detected
        "header": str|null, # Header content when using `extract_header=True`
        "footer": str|null, # Footer content when using `extract_footer=True`
        "dimensions": dict # The dimensions of the page
        }
    ],
    "model": str, # The model used for the OCR
    "document_annotation": dict|null, # Document annotation information when used, visit the Annotations documentation for more information
    "usage_info": dict # Usage information
    }
See https://docs.mistral.ai/capabilities/document_ai/basic_ocr for more details.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `api_key` | `str` | `` | a mistral ai api key |
| `output_keys` | `list[str]` | `"lambda: ['documents', 'filepath']()"` |  |
| `model` | `str` | `'mistral-ocr-latest'` | Mistral OCR model name |
| `include_image_base64` | `bool` | `False` | Whether OCR page payloads should include embedded base64 images |


```python
# Example usage of `LLMOCRAction`
from pydag.nodes.llm.LLMOCRAction import LLMOCRAction  # Adjust import if needed

obj = LLMOCRAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.api_key="<string>"
obj.output_keys="lambda: ['documents', 'filepath']()"
obj.model='mistral-ocr-latest'
obj.include_image_base64=False
```

[Go to Summary](#summary)
## `LLMScriptElement` (in `pydag\nodes\llm\LLMScriptElement.py`)

`DataElement` to generate Code for data processing using LLM on a specified input
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `system_message` | `str` | `'SYS_PYTHON_EXPERT'` | Default System message to give to the LLM Agent |
| `human_msg` | `str` | `` | Human message to give to the LLM Agent for generating code |
| `service_id` | `str` | `` | unique id of the LLM service required for this DataElement |


```python
# Example usage of `LLMScriptElement`
from pydag.nodes.llm.LLMScriptElement import LLMScriptElement  # Adjust import if needed

obj = LLMScriptElement()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.system_message='SYS_PYTHON_EXPERT'
obj.human_msg="<string>"
obj.service_id="<string>"
```

[Go to Summary](#summary)
## `FFTTransform` (in `pydag\nodes\preprocessing\frequency\FFTTransform.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `FFTTransform`
from pydag.nodes.preprocessing.frequency.FFTTransform import FFTTransform  # Adjust import if needed

obj = FFTTransform()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ZScore` (in `pydag\nodes\preprocessing\statistics\ZScore.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `ZScore`
from pydag.nodes.preprocessing.statistics.ZScore import ZScore  # Adjust import if needed

obj = ZScore()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `TrendWindowNode` (in `pydag\nodes\preprocessing\windowing\TrendWindowNode.py`)

This `BufferNode` collects windowed data of the linked parents of specified size `n` with the current timestamp as key prefix to the original key.
Whenever it is executed it generates a new window to keep (up to `max_windows`). If the maximum number of windows are reached, it discards the one closest to any other window, based on timestamp.

Base Classes:
    BufferNode (_type_): _description_
    Action (_type_): _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `max_windows` | `int` | `10` | number of windows to keep |
| `date_format` | `str` | `'%Y-%m-%d %H:%M:%S'` | dateformat to convert the new keys to |
| `date_separator` | `str` | `'#'` | separator for splitting original key and timestamp, this should never be a word/character that could exist in the date_format |


```python
# Example usage of `TrendWindowNode`
from pydag.nodes.preprocessing.windowing.TrendWindowNode import TrendWindowNode  # Adjust import if needed

obj = TrendWindowNode()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.max_windows=10
obj.date_format='%Y-%m-%d %H:%M:%S'
obj.date_separator='#'
```

[Go to Summary](#summary)
## `RegressionTransform` (in `pydag\nodes\regression\RegressionTransform.py`)

Code Service to do Regression on Inputs
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `min_learning_samples` | `int` | `0` | Minimum number of samples required for learning. |
| `min_inference_samples` | `int` | `0` | Number of Samples to do inference on. |
| `sample_length` | `int` | `0` | Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed. |
| `normalize` | `bool` | `False` | Flag to indicate whether to normalize the input data using z-score normalization on the input batch. |
| `nan_to_num` | `bool` | `False` | If True, replace NaN/Inf values with finite numbers (0.0). |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `model_name` | `str` | `'Tirex'` | name of the model to use for regression. Default is Tirex |
| `learning_required` | `bool` | `True` | whether the model requires a learning phase before inference |
| `prediction_length` | `int` | `64` | length of the prediction horizon |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output keys; if empty, default naming is used |


```python
# Example usage of `RegressionTransform`
from pydag.nodes.regression.RegressionTransform import RegressionTransform  # Adjust import if needed

obj = RegressionTransform()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.min_learning_samples=0
obj.min_inference_samples=0
obj.sample_length=0
obj.normalize=False
obj.nan_to_num=False
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.model_name='Tirex'
obj.learning_required=True
obj.prediction_length=64
obj.output_keys='list()'
```

[Go to Summary](#summary)
## `ScriptAction` (in `pydag\nodes\script\ScriptAction.py`)

`Action` for executing a custom script to process data from the parents' `Buffer`s and to store the processed data back into this `Buffer`.
<br>The script must be a valid Python code snippet that runs properly.
<br>The function takes the current buffer data and injects data from it by the specified `input_keys`.
<br>The same way the `Action`returns data by the specified `output_keys` back to its `Buffer`.
<br>Note that the script is executed in its own local scope, so variables defined in the script do not interfere with variables outside the script.
<br>Also note that all output variables should be converted to primitives (e.g. int, float, str, list, dict) or list of primitives inside the script. Do not leave them as numpy arrays or dataframes.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `script_path` | `str` | `` | Python code snippet defining a script to process buffer data |
| `output_keys` | `list[str]` | `'list()'` | keys to extract from the script and store their values into this element's buffer. If empty, no data is stored in the buffer. |
| `use_parent_data` | `bool` | `True` | whether to use data from parent buffers. If set to false, the script will only receive data from its own buffer. This can be useful if you want to execute a script that does not depend on parent data, but you still may want to use the output_keys to store data in the buffer. |


```python
# Example usage of `ScriptAction`
from pydag.nodes.script.ScriptAction import ScriptAction  # Adjust import if needed

obj = ScriptAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.script_path="<string>"
obj.output_keys='list()'
obj.use_parent_data=True
```

[Go to Summary](#summary)
## `FileTriggerAction` (in `pydag\nodes\triggers\FileTriggerAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `service_id` | `str` | `` | ID of the service |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `folder` | `str` | `` | folder to wach for file events |
| `recursive` | `bool` | `False` | listen to events in subfolders as well |
| `create_events` | `bool` | `True` | listen to create events |
| `modified_events` | `bool` | `False` | listen to modified events |
| `moved_events` | `bool` | `False` | listen to moved events |
| `delete_events` | `bool` | `False` | listen to delete events |
| `output_keys` | `list[str]` | `"lambda: ['filepaths']()"` | default output key |


```python
# Example usage of `FileTriggerAction`
from pydag.nodes.triggers.FileTriggerAction import FileTriggerAction  # Adjust import if needed

obj = FileTriggerAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.service_id="<string>"
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.folder="path/to/folder"
obj.recursive=False
obj.create_events=True
obj.modified_events=False
obj.moved_events=False
obj.delete_events=False
obj.output_keys="lambda: ['filepaths']()"
```

[Go to Summary](#summary)
## `ObserverTriggerAction` (in `pydag\nodes\triggers\ObserverTriggerAction.py`)

A `TriggerAction`, that connects to a `ObserverService` and executes the `Observer` notification everytime the
trigger event occurs. This `Node` does not define `start_trigger`, but rather expects being triggered externally from application or for example REST API.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `ObserverTriggerAction`
from pydag.nodes.triggers.ObserverTriggerAction import ObserverTriggerAction  # Adjust import if needed

obj = ObserverTriggerAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ConfigureElementAction` (in `pydag\nodes\utils\ConfigureElementAction.py`)

this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property
<br>the new property value is derived from the `Node`'s `buffer`

Args:
    GrabberNode (_type_): inherits from class GrabberNode
    BufferNode (_type_): inherits from class BufferNode

Raises:
    StatemachineException: if an error occurs during execute
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `option` | `str` | `` | option to configure with new value |
| `element_id` | `str` | `` | id of the element to change the option for |


```python
# Example usage of `ConfigureElementAction`
from pydag.nodes.utils.ConfigureElementAction import ConfigureElementAction  # Adjust import if needed

obj = ConfigureElementAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.option="<string>"
obj.element_id="<string>"
```

[Go to Summary](#summary)
## `CountAction` (in `pydag\nodes\utils\CountAction.py`)

Action that counts the number of times it has been called.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `CountAction`
from pydag.nodes.utils.CountAction import CountAction  # Adjust import if needed

obj = CountAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CountTransition` (in `pydag\nodes\utils\CountTransition.py`)

A transition that counts the number of times it has been triggered.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `CountTransition`
from pydag.nodes.utils.CountTransition import CountTransition  # Adjust import if needed

obj = CountTransition()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `FalseTransition` (in `pydag\nodes\utils\FalseTransition.py`)

A transition that always returns False.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `FalseTransition`
from pydag.nodes.utils.FalseTransition import FalseTransition  # Adjust import if needed

obj = FalseTransition()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `JoinTransition` (in `pydag\nodes\utils\JoinTransition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `JoinTransition`
from pydag.nodes.utils.JoinTransition import JoinTransition  # Adjust import if needed

obj = JoinTransition()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `MailAction` (in `pydag\nodes\utils\MailAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `smtp_server` | `str` | `` | host of the mail server to use |
| `port` | `int` | `` | port of the smtp server |
| `mail_account` | `str` | `` | mail account to use for login |
| `pw` | `str` | `` | password of the mail server |
| `recipients` | `str | list[str]` | `'list[str]()'` | mail address of the recipient |
| `subject` | `str` | `` | subject of the mail |
| `body` | `str` | `` | body of the mail |
| `tls` | `bool` | `True` | use TLS for the connection |
| `debug_mode` | `bool` | `False` | if set to true, no mails are send, but only logged to console |


```python
# Example usage of `MailAction`
from pydag.nodes.utils.MailAction import MailAction  # Adjust import if needed

obj = MailAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.smtp_server="<string>"
obj.port=1
obj.mail_account="<string>"
obj.pw="<string>"
obj.recipients='list[str]()'
obj.subject="<string>"
obj.body="<string>"
obj.tls=True
obj.debug_mode=False
```

[Go to Summary](#summary)
## `MailBufferAction` (in `pydag\nodes\utils\MailBufferAction.py`)

An `Action` that send emails based on data from parent `Buffer`.

This action expects the parent buffer to provide exactly three input keys
(in this fixed order): `recipients`, `subject`, and `body`.

Behavior:
    - `recipients` may be a single email address (string) or a comma-separated
        string / list of addresses accepted by the underlying SMTP `sendmail` call.
    - `subject` and `body` are used to populate the message's Subject header
        and HTML body respectively.
    - The action connects to `smtp_server`:`port` and optionally starts TLS
        (when `tls` is True). If `pw` is provided the action will attempt to
        authenticate using `mail_account`/`pw`.
    - When `debug_mode` is True, messages are not sent but logged for
        inspection.

Raises:
        NodeException: if input keys are missing/invalid or if sending fails.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `smtp_server` | `str` | `` | host of the mail server to use |
| `port` | `int` | `` | port of the smtp server |
| `mail_account` | `str` | `` | mail account to use for login |
| `pw` | `str` | `` | password of the mail server |
| `tls` | `bool` | `True` | use TLS for the connection |
| `debug_mode` | `bool` | `False` | if set to true, no mails are send, but only logged to console |
| `input_keys` | `list[str]` | `"lambda: ['recipients', 'subject', 'body']()"` | the input keys must be 3 in total and in the fixed order: recipients, subject and body |
| `persistent` | `bool` | `False` | by default, sent mails are removed from buffer |
| `n` | `int` | `0` | all buffer samples are extracted at once |


```python
# Example usage of `MailBufferAction`
from pydag.nodes.utils.MailBufferAction import MailBufferAction  # Adjust import if needed

obj = MailBufferAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.smtp_server="<string>"
obj.port=1
obj.mail_account="<string>"
obj.pw="<string>"
obj.tls=True
obj.debug_mode=False
obj.input_keys="lambda: ['recipients', 'subject', 'body']()"
obj.persistent=False
obj.n=0
```

[Go to Summary](#summary)
## `OSKillProcessAction` (in `pydag\nodes\utils\OSKillProcessAction.py`)

`Node` that kills a specified OS process by its executable name.

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `executable` | `str` | `` | The executable to kill, e.g. 'python.exe' |


```python
# Example usage of `OSKillProcessAction`
from pydag.nodes.utils.OSKillProcessAction import OSKillProcessAction  # Adjust import if needed

obj = OSKillProcessAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.executable="<string>"
```

[Go to Summary](#summary)
## `OSProcessAction` (in `pydag\nodes\utils\OSProcessAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `executable` | `str` | `` | The executable to run, e.g., 'python.exe' |
| `arguments` | `list` | `'list()'` | List of arguments to pass to the executable |
| `detached` | `bool` | `True` | Whether to run the process in a detached state |
| `encoding` | `str` | `'cp850'` | force utf-8, cp1252 or cp850 decoding, cp850 works on german windows systems |


```python
# Example usage of `OSProcessAction`
from pydag.nodes.utils.OSProcessAction import OSProcessAction  # Adjust import if needed

obj = OSProcessAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.executable="<string>"
obj.arguments='list()'
obj.detached=True
obj.encoding='cp850'
```

[Go to Summary](#summary)
## `PrintAction` (in `pydag\nodes\utils\PrintAction.py`)

An action that prints a message when executed.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `message` | `str` | `` |  |


```python
# Example usage of `PrintAction`
from pydag.nodes.utils.PrintAction import PrintAction  # Adjust import if needed

obj = PrintAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.message="<string>"
```

[Go to Summary](#summary)
## `PrintBufferAction` (in `pydag\nodes\utils\PrintBufferAction.py`)

utility `Action` to print the parents' results

Args:
    BufferNode (_type_): _description_
    Action (_type_): _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `PrintBufferAction`
from pydag.nodes.utils.PrintBufferAction import PrintBufferAction  # Adjust import if needed

obj = PrintBufferAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `SleepAction` (in `pydag\nodes\utils\SleepAction.py`)

An action that sleeps for a specified number of seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `sleep_time` | `int` | `0` | number of seconds to sleep for |


```python
# Example usage of `SleepAction`
from pydag.nodes.utils.SleepAction import SleepAction  # Adjust import if needed

obj = SleepAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.sleep_time=0
```

[Go to Summary](#summary)
## `SleepUntilAction` (in `pydag\nodes\utils\SleepUntilAction.py`)

An action that sleeps until the specified daytime.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `daytime` | `str` | `` | day time when the sleep should end, format hh:mm:ss |


```python
# Example usage of `SleepUntilAction`
from pydag.nodes.utils.SleepUntilAction import SleepUntilAction  # Adjust import if needed

obj = SleepUntilAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.daytime="<string>"
```

[Go to Summary](#summary)
## `StartAction` (in `pydag\nodes\utils\StartAction.py`)

An action that starts the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `StartAction`
from pydag.nodes.utils.StartAction import StartAction  # Adjust import if needed

obj = StartAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `StopAction` (in `pydag\nodes\utils\StopAction.py`)

An action that stops the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `StopAction`
from pydag.nodes.utils.StopAction import StopAction  # Adjust import if needed

obj = StopAction()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `TrueTransition` (in `pydag\nodes\utils\TrueTransition.py`)

A transition that always returns True.
This is used to test the statemachine without any conditions.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `TrueTransition`
from pydag.nodes.utils.TrueTransition import TrueTransition  # Adjust import if needed

obj = TrueTransition()
obj.child_ids='list()'
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `OCRAction` (in `pydag\nodes\vision\OCRAction.py`)

`Action` to perform OCR on images or pdfs that loaded from filepaths of parent `BufferNode`s and stored as extracted text in its `Buffer`.

the action outputs extracted text and the source path with the keys ["path", "text"]

Requirements:
- make sure poopler is installed and on PATH (in windows)
https://github.com/oschwartz10612/poppler-windows/releases/tag/v25.11.0-0
- make sure tesseract is installed and on PATH (in windows)
https://tesseract-ocr.github.io/tessdoc/Installation.html and https://github.com/UB-Mannheim/tesseract/wiki (for windows)
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `path_key` | `str` | `'path'` | Key for the source file path in the output dictionary. |
| `text_key` | `str` | `'text'` | Key for text output in the output dictionary. |


```python
# Example usage of `OCRAction`
from pydag.nodes.vision.OCRAction import OCRAction  # Adjust import if needed

obj = OCRAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.path_key='path'
obj.text_key='text'
```

[Go to Summary](#summary)
## `BrowserAutomationAction` (in `pydag\nodes\webbrowser\BrowserAutomationAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `BrowserAutomationAction`
from pydag.nodes.webbrowser.BrowserAutomationAction import BrowserAutomationAction  # Adjust import if needed

obj = BrowserAutomationAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
```

[Go to Summary](#summary)
## `BrowserClickElementAction` (in `pydag\nodes\webbrowser\BrowserClickElementAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `xpath` | `str` | `` | XPath definition to locate the element to get a value from |
| `wait` | `int` | `0` | maximum wait time before the UI element is accessed |
| `scroll_into_view` | `bool` | `False` | scrolls the element into view before attempting click |
| `force_click` | `bool` | `False` | forces click via javascript |
| `wait_for_modal` | `str` | `` | waits for the modal element specified by class |


```python
# Example usage of `BrowserClickElementAction`
from pydag.nodes.webbrowser.BrowserClickElementAction import BrowserClickElementAction  # Adjust import if needed

obj = BrowserClickElementAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.xpath="<string>"
obj.wait=0
obj.scroll_into_view=False
obj.force_click=False
obj.wait_for_modal="<string>"
```

[Go to Summary](#summary)
## `BrowserGetElementAction` (in `pydag\nodes\webbrowser\BrowserGetElementAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `xpath` | `str` | `` | XPath definition to locate the element to get a value from |
| `attribute` | `str` | `` | specifies the name of the attribute to retrieve data from, defaults to None, then only the inner text of element is retrieved |
| `output_keys` | `list[str]` | `"lambda: ['tags', 'values']()"` |  |


```python
# Example usage of `BrowserGetElementAction`
from pydag.nodes.webbrowser.BrowserGetElementAction import BrowserGetElementAction  # Adjust import if needed

obj = BrowserGetElementAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.buffer_id="<string>"
obj.persistent=True
obj.n=0
obj.input_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.xpath="<string>"
obj.attribute="<string>"
obj.output_keys="lambda: ['tags', 'values']()"
```

[Go to Summary](#summary)
## `BrowserSetElementAction` (in `pydag\nodes\webbrowser\BrowserSetElementAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `input_keys` | `list[str] | list[int] | str` | `'list()'` | list of input key names used to extract data from parent buffers. input_keys can also be a list of integers for indices or a Python-style slice string (e.g. '-1' for last index, '1:3' or '0:5:2' for start:stop:step exclusive indexing), or a type selector ('type:string' for text-like values, 'type:number' for numeric and bool values). Duplicates are removed while preserving first-match order. If empty, all parent keys are returned |
| `output_keys` | `list[str]` | `'list()'` | optional explicit output key names written by this node. output_keys are literal names only and do not support selector syntax. If empty, the node uses its default output naming |
| `ignore_keys` | `list[str]` | `'list()'` | list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys |
| `ignore_empty_parents` | `bool` | `True` | if True then, empty data returns from parent do not throw a NodeException and just return an empty dict (default: True) |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `xpath` | `str` | `` | XPath definition to locate the element to set a value to |
| `persistent` | `bool` | `False` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `1` | specifies how much data is retrieved from parent buffer. Here Default 1 -> only one value per Set Action |


```python
# Example usage of `BrowserSetElementAction`
from pydag.nodes.webbrowser.BrowserSetElementAction import BrowserSetElementAction  # Adjust import if needed

obj = BrowserSetElementAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.buffer_id="<string>"
obj.input_keys='list()'
obj.output_keys='list()'
obj.ignore_keys='list()'
obj.ignore_empty_parents=True
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.xpath="<string>"
obj.persistent=False
obj.n=1
```

[Go to Summary](#summary)
## `BrowserUrlNavigateAction` (in `pydag\nodes\webbrowser\BrowserUrlNavigateAction.py`)

`Action` for navigating a Browser Automation Object to a new url

Raises:
    NodeException: if referenced `self._service`  is not of type `BrowserAutomationService`
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service |
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `url` | `str` | `` | url to navigate to in browser |
| `sleep_time` | `float` | `0.0` | time to wait after navigation (in seconds) |


```python
# Example usage of `BrowserUrlNavigateAction`
from pydag.nodes.webbrowser.BrowserUrlNavigateAction import BrowserUrlNavigateAction  # Adjust import if needed

obj = BrowserUrlNavigateAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.id=<dataclasses._MISSING_TYPE object at 0x000001E5AD05D100>
obj.load_on_install=False
obj.url="https://example.com"
obj.sleep_time=0.0
```

[Go to Summary](#summary)
