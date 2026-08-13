from dataclasses import dataclass, field
from datetime import datetime
import enum
from pathlib import Path
import shutil
from loguru import logger

from ..ServiceException import ServiceException
from ...utils.FileUtils import FileUtils
from ..Observer import Observer
from ...agents.Agent import Agent
from ..ObserverService import ObserverService

class DiscardMode(str, enum.Enum):
    EQUIDISTANT = "equidistant"
    OLDEST = "oldest"

@dataclass
class Backup:
    path : Path
    timestamp : datetime

@dataclass
class RollingBackupService(ObserverService):
    
    source : list[str] | str = field(default_factory=list, metadata={"description": "a list or single folder path or filepath of which backups shall be made"})
    target : str = field(default=None, metadata={"description": "target folder to store the backups"})
    max_backups : int = field(default=0, metadata={"description": "defaults to 0, which means no maximum amount"})
    discard_mode : str = field(default=DiscardMode.EQUIDISTANT.value, metadata={"description": f"specifies how to discard backups if the `max_backups` property is exceeded, options are: {" | ".join(member.value for member in DiscardMode)}"})
    backup_date_prefix : str = field(default="%Y%m%d%H%M%S", metadata={"description": "timestamp formatted in the specified way, that is attached in front of filename"})
    zipped : bool = field(default=False, metadata={"description": "specifies whether the backup files are being zipped in target"})
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self.source is None:
            raise ServiceException("No source was specified")
        if self.target is None:
            raise ServiceException("No target was specified")
        if isinstance(self.source, str):
            self.source = [self.source]
        tp : Path = Path(self.target)
        tp.mkdir(parents=True, exist_ok=True)
        self.add_observer(RollingBackupObserver(self))

class RollingBackupObserver(Observer):
    """
    Observer to handle the folder observation logic.
    """
        
    def __init__(self, service : RollingBackupService):
        super().__init__()
        self._service = service
                
    def observe(self):
        timestamp = datetime.now()
        logger.info(f"Starting backup at {timestamp.isoformat()}")
        tp : Path = Path(self._service.target)
        # backing up each source
        for s in self._service.source:
            sp = Path(s)
            if not sp.exists():
                logger.warning(f"Source does not exist: {s}")
                continue
            ts : str = timestamp.strftime(self._service.backup_date_prefix)    
            if self._service.zipped:
                backup_name = f"{ts}_{sp.stem}"                        
                archive_path = (tp / f"{backup_name}.zip")
                FileUtils.compress(sp, archive_path)
                logger.info(f"Created backup: {archive_path}")
            else:
                backup_name = f"{ts}_{sp.name}" 
                np = (tp / backup_name)
                if sp.is_dir():
                    shutil.copytree(sp, np)
                else:
                    shutil.copy2(sp, np)
                logger.info(f"Created backup: {tp}")
        # cleanup backups
        if self._service.max_backups > 0:
            backups : list[Backup] = self._find_backups(tp)
            backup_dic : dict[str, list[Backup]] = self._split_backups(backups)
            if len(backups) > self._service.max_backups:
                match (DiscardMode(self._service.discard_mode)):
                    case DiscardMode.EQUIDISTANT:
                        self._cleanup_equidistant(backup_dic)
                    case DiscardMode.OLDEST:
                        self._cleanup_oldest(backup_dic)
        
    def unobserve(self):
        return
    
    def _find_backups(self, backup_path : Path) ->  list[Backup]:
        backups : list[Backup] = []
        for p in backup_path.iterdir():
            ts : datetime = self._extract_timestamp(p.name)
            if ts:
                backups.append(Backup(path=p, timestamp=ts))
        backups.sort(key=lambda x: x.timestamp)
        return backups 
                
    def _extract_timestamp(self, filename : str) -> datetime:
        timestamp_string : str = filename.split("_")[0]
        try:
            return datetime.strptime(timestamp_string, self._service.backup_date_prefix)
        except ValueError:
            return None
    
    def _delete_backup(self, backup: Backup):
        path = backup.path
        logger.info(f"Deleting backup: {path}")
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    
    def _split_backups(self, backups : list[Backup]) -> dict[str, list[Backup]]:
        d : dict[str, list] = dict()
        for b in backups:
            p : Path = b.path
            fn : str = "_".join(p.name.split("_")[1:])
            if fn in d:
                d[fn].append(b)
            else:
                d[fn] = [b]
        return d
            
    def _cleanup_equidistant(self, backup_dic: dict[str, list[Backup]]):
        for key, backups in backup_dic.items():
            while len(backups) > self._service.max_backups:
                index = self._find_closest_pair(backups)

                # Remove the newer item of the closest pair.
                #
                # Keeping the older item gives us a better
                # representation of the earlier point in time.
                
                # always keep last
                #if index + 1 == len(backups) - 1:
                #    remove_index = index   
                #else:
                remove_index = index + 1
                
                backup = backups.pop(remove_index)
                self._delete_backup(backup)
    
    def _cleanup_oldest(self, backup_dic: dict[str, list[Backup]]):
        for key, backups in backup_dic.items():
            while len(backups) > self._service.max_backups:
                backup = backups.pop(0)
                self._delete_backup(backup)
    
    @staticmethod            
    def _find_closest_pair(backups: list[Backup]) -> int:
        smallest_difference = None
        smallest_index : int = 0
        for i in range(0, len(backups) - 1):
            difference = (backups[i + 1].timestamp - backups[i].timestamp)

            if (smallest_difference is None or difference < smallest_difference):
                smallest_difference = difference
                smallest_index = i
        return smallest_index