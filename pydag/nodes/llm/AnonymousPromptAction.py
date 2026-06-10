import hashlib
import re
import secrets
from dataclasses import dataclass, field
import spacy
from spacy.language import Language

from pydag.nodes.NodeException import NodeException


from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class AnonymousPromptAction(BufferNode, Action):
    """ `BufferNode` `Action` for anonymizing prompts by hashing sensitive information like emails, phone numbers, urls, bank details, addresses and names.
        The hashing is done with a salt to ensure that the same input will always produce the same output, but different inputs will produce different outputs.
        This allows for consistent anonymization while preventing reverse engineering of the original data.
        This class requires the spacy model "de_core_news_lg" to be installed for entity recognition.
        Download with: python -m spacy download de_core_news_lg 
    """
    
    mails : bool = field(default=True, metadata={"description": "Whether to anonymize email addresses."})
    phones : bool = field(default=True, metadata={"description": "Whether to anonymize phone numbers."})
    urls : bool = field(default=True, metadata={"description": "Whether to anonymize URLs."})
    bank_details : bool = field(default=True, metadata={"description": "Whether to anonymize bank details."})
    addresses_names : bool = field(default=True, metadata={"description": "Whether to anonymize addresses and names."})
    lang : str = field(default="de", metadata={"description": "language pack for spacy, de | en"})
    
    def __post_init__(self):
        super().__post_init__()
        self._mappings : dict = {}
        self._salt : str = secrets.token_hex(32)
        self._nlp : Language = None
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        match self.lang:
            case "en":
                self._nlp = spacy.load("en_core_web_lg")
            case "de":
                self._nlp = spacy.load("de_core_news_lg")
            case _:
                raise NodeException(f"Could not load language pack from spacy for lang={self.lang}")
        
        
    def _on_execute(self):
        data = self.get_parent_data(by_rows=True)
        row : dict
        for row in data:
            for key, value in row.items():
                if isinstance(value, str):
                    row[key] = self._anonymize(value)
            self.add_data(row)
    
    def _anonymize(self, text: str) -> str:
        """ Anonymizes the input text by hashing sensitive information based on the initialized settings. """
        # Anonymizes the input text by hashing sensitive information based on the initialized settings.
        if self.mails:
            text = self._hash_emails(text)
        if self.bank_details:
            text = self._hash_bank_details(text)
        if self.phones:
            text = self._hash_phone_numbers(text)
        if self.urls:
            text = self._hash_urls(text)
        if self.addresses_names:
            text = self._hash_addresses_and_names(text)
        return text
    
    @staticmethod
    def _hash_value(value: str, salt : str = None) -> str:
        normalized = value.strip().lower()
        if salt:
            return hashlib.sha256((salt + normalized).encode()).hexdigest()[:12]
        else:
            return hashlib.sha256(normalized.encode()).hexdigest()[:12]
    
    def _hash_emails(self, text: str) -> str:
        
        def replacer(m):
            original = m.group()
            hashed = f"<EMAIL_{AnonymousPromptAction._hash_value(original, self._salt)}>"
            self._mappings[hashed] = original  # store mapping
            return hashed
            
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            replacer,
            text
        )
        return text
    
    
    def _hash_phone_numbers(self, text: str) -> str:
        
        def normalize_phone(phone : str) -> str:
            return phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
        text = re.sub(
            r'\+?\d{1,3}[\s\-]?\(?\d{2,5}\)?[\s\-]?\d{3,}\d*',
            lambda m: f"<PHONE_{AnonymousPromptAction._hash_value(normalize_phone(m.group()), self._salt)}>",
            text
        )
        return text
    
    def _hash_urls(self, text: str) -> str:
        text = re.sub(
            r'(https?://[^\s]+|www\.[^\s]+)',
            lambda m: f"<URL_{AnonymousPromptAction._hash_value(m.group(), self._salt)}>",
            text
        )
        return text
    
    def _hash_bank_details(self, text: str) -> str:
        
        def normalize_iban(iban : str) -> str:
            return re.sub(r"\s+", "", iban).upper()
    
        # IBAN (simplified, real IBAN validation is more complex)
        text = re.sub(
            r'\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{1,4}){2,10}\b',
            lambda m: f"<IBAN_{AnonymousPromptAction._hash_value(normalize_iban(m.group()), self._salt)}>",
            text
        )
        # BIC / SWIFT
        text = re.sub(
            r'\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
            lambda m: f"<BIC_{AnonymousPromptAction._hash_value(m.group(), self._salt)}>",
            text
        )
        return text
    
    def _hash_addresses_and_names(self, text: str) -> str:
        doc = self._nlp(text)

        # process entities in reverse order to avoid offset shifts
        for ent in sorted(doc.ents, key=lambda e: e.start_char, reverse=True):

            if ent.label_ in ["PER", "PERSON"]:
                token = f"<NAME_{AnonymousPromptAction._hash_value(ent.text, self._salt)}>"

            elif ent.label_ in ["LOC", "GPE", "ORG"]:
                token = f"<{ent.label_}_{AnonymousPromptAction._hash_value(ent.text, self._salt)}>"

            else:
                continue

            text = text[:ent.start_char] + token + text[ent.end_char:]

        return text
    
        