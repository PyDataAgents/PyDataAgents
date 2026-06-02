import hashlib
import re
import secrets

import spacy


class AnonymousPrompt:
    """ Helper Class for anonymizing prompts by hashing sensitive information like emails, phone numbers, urls, bank details, addresses and names.
        The hashing is done with a salt to ensure that the same input will always produce the same output, but different inputs will produce different outputs.
        This allows for consistent anonymization while preventing reverse engineering of the original data.
        This class requires the spacy model "de_core_news_lg" to be installed for entity recognition.
        Download with: python -m spacy download de_core_news_lg
        """
    
    def __init__(self, mails : bool = True, phones : bool = True, urls : bool = True, bank_details : bool = True, addresses_names : bool = True):
        self._mails : bool = mails
        self._phones : bool = phones
        self._urls : bool = urls
        self._bank_details : bool = bank_details
        self._addresses_names : bool = addresses_names
        self._mappings : dict = {}
        self._salt : str = secrets.token_hex(32)

    def anonymize(self, text: str) -> str:
        """ Anonymizes the input text by hashing sensitive information based on the initialized settings. """
        if self._mails:
            text = self._hash_emails(text)
        if self._bank_details:
            text = self._hash_bank_details(text)
        if self._phones:
            text = self._hash_phone_numbers(text)
        if self._urls:
            text = self._hash_urls(text)
        if self._addresses_names:
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
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            lambda m: f"<EMAIL_{AnonymousPrompt._hash_value(m.group(), self._salt)}>",
            text
        )
        return text
    
    
    def _hash_phone_numbers(self, text: str) -> str:
        
        def normalize_phone(phone : str) -> str:
            return phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
        text = re.sub(
            r'\+?\d{1,3}[\s\-]?\(?\d{2,5}\)?[\s\-]?\d{3,}\d*',
            lambda m: f"<PHONE_{AnonymousPrompt._hash_value(normalize_phone(m.group()), self._salt)}>",
            text
        )
        return text
    
    def _hash_urls(self, text: str) -> str:
        text = re.sub(
            r'(https?://[^\s]+|www\.[^\s]+)',
            lambda m: f"<URL_{AnonymousPrompt._hash_value(m.group(), self._salt)}>",
            text
        )
        return text
    
    def _hash_bank_details(self, text: str) -> str:
        
        def normalize_iban(iban : str) -> str:
            return re.sub(r"\s+", "", iban).upper()
    
        # IBAN (simplified, real IBAN validation is more complex)
        text = re.sub(
            r'\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{1,4}){2,10}\b',
            lambda m: f"<IBAN_{AnonymousPrompt._hash_value(normalize_iban(m.group()), self._salt)}>",
            text
        )
        # BIC / SWIFT
        text = re.sub(
            r'\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
            lambda m: f"<BIC_{AnonymousPrompt._hash_value(m.group(), self._salt)}>",
            text
        )
        return text
    
    def _hash_addresses_and_names(self, text: str) -> str:
        nlp = spacy.load("de_core_news_lg")
        doc = nlp(text)

        # process entities in reverse order to avoid offset shifts
        for ent in sorted(doc.ents, key=lambda e: e.start_char, reverse=True):

            if ent.label_ in ["PER", "PERSON"]:
                token = f"<NAME_{AnonymousPrompt._hash_value(ent.text, self._salt)}>"

            elif ent.label_ in ["LOC", "GPE", "ORG"]:
                token = f"<{ent.label_}_{AnonymousPrompt._hash_value(ent.text, self._salt)}>"

            else:
                continue

            text = text[:ent.start_char] + token + text[ent.end_char:]

        return text
    
        