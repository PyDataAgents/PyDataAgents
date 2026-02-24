import os
from pathlib import Path
import shutil as sh
from pydag.utils.FileUtils import FileUtils

# Inputs expected from ScriptAction local scope:
# - folder_name: str — name of the folder to create under Downloads

# Outputs produced for ScriptAction to capture via output_keys:
# - folder_path: str — full path to the created/existing folder
# - created: bool — True if the folder was created by this run, False if it already existed

# Retrieve the folder name from the injected local scope. Adjust here if you
# pass a different key name via ScriptAction.input_keys (e.g., "name").

try:
	if isinstance(answer, list):
		if len(answer) > 0:
			_folder_name = str(answer[0])
		else:
			_folder_name = None
	else:
		_folder_name = None


	if _folder_name is None or _folder_name.strip() == "":
		raise ValueError("No valid folder name provided in local scope (expected 'folder_name' or 'name').")


	target_path = Path(FileUtils.user_home() + os.sep + "Downloads" + os.sep + _folder_name)
		
	created = False
	if not target_path.exists():
		target_path.mkdir(parents=True, exist_ok=True)
		created = True

	# Outputs for ScriptAction
	answer = str(_folder_name)


	with open(Path(target_path / f"{answer}.txt"), "w", encoding="utf-8") as f:
		f.write(f"Folder '{_folder_name}' created at {target_path}\n")
		f.write(f"document_content: {documents}\n")

	# move file to target folder
	sh.copy(str(filepath[0]), str(target_path / Path(filepath[0]).name)) 
	#sh.move(str(filepath[0]), str(target_path / Path(filepath[0]).name))

except:
	pass



