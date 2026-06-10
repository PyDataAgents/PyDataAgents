from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.llm.AnonymousPromptAction import AnonymousPromptAction

TEXT_EN = """
        OFFER / QUOTATION

        Offer No.: 2026-015
        Date: 09 June 2026

        Supplier

        TechSolutions GmbH
        Musterstraße 12
        72458 Albstadt
        Germany

        Contact:
        Max Mustermann
        Sales Manager
        Email: max.mustermann@techsolutions.de
        Phone: +49 7431 123456

        Customer

        Innovatech AG
        Industriestraße 45
        70173 Stuttgart
        Germany

        Contact:
        Anna Schneider
        Procurement Manager
        Email: anna.schneider@innovatech.de

        Subject

        Supply and installation of precision measurement equipment

        Offer Details
        Pos.	Description	Qty	Unit Price (€)	Total (€)
        1	Digital Caliper (0–150 mm)	10	45.00	450.00
        2	Precision Scale (0–5 kg)	5	120.00	600.00
        3	Installation & Calibration Service	1	300.00	300.00

        Subtotal: €1,350.00
        VAT (19%): €256.50
        Total Amount: €1,606.50

        Delivery Terms
        Delivery time: 2–3 weeks after order confirmation
        Delivery method: Standard shipping (DAP Stuttgart)
        Payment Terms
        30% advance payment upon order confirmation
        70% within 14 days after delivery
        Payment via bank transfer

        Bank Details:
        Bank: Deutsche Bank
        IBAN: DE89 3704 0044 0532 0130 00
        BIC: COBADEFFXXX

        Validity

        This offer is valid until 30 June 2026.

        Additional Notes
        Installation scheduled upon agreement
        Warranty: 12 months from delivery date

        We appreciate your interest in our products and look forward to your order.

        Kind regards,

        Max Mustermann
        TechSolutions GmbH
    """
    
TEXT_DE = """
    ANGEBOT

    Angebots-Nr.: 2026-015
    Datum: 09. Juni 2026

    Anbieter

    TechSolutions GmbH
    Musterstraße 12
    72458 Albstadt
    Deutschland

    Ansprechpartner:
    Max Mustermann
    Vertriebsleiter
    E-Mail: max.mustermann@techsolutions.de
    Telefon: +49 7431 123456

    Kunde

    Innovatech AG
    Industriestraße 45
    70173 Stuttgart
    Deutschland

    Ansprechpartnerin:
    Anna Schneider
    Einkaufsleiterin
    E-Mail: anna.schneider@innovatech.de

    Betreff

    Lieferung und Installation von Präzisionsmessgeräten

    Angebotspositionen
    Pos.	Beschreibung	Menge	Einzelpreis (€)	Gesamt (€)
    1	Digitaler Messschieber (0–150 mm)	10	45,00	450,00
    2	Präzisionswaage (0–5 kg)	5	120,00	600,00
    3	Installation & Kalibrierung	1	300,00	300,00

    Zwischensumme: 1.350,00 €
    MwSt. (19 %): 256,50 €
    Gesamtbetrag: 1.606,50 €

    Lieferbedingungen
    Lieferzeit: 2–3 Wochen nach Auftragseingang
    Lieferung: Standardversand (DAP Stuttgart)
    Zahlungsbedingungen
    30 % Anzahlung bei Auftragserteilung
    70 % innerhalb von 14 Tagen nach Lieferung
    Zahlung per Banküberweisung

    Bankverbindung:
    Bank: Deutsche Bank
    IBAN: DE89 3704 0044 0532 0130 00
    BIC: COBADEFFXXX

    Gültigkeit

    Dieses Angebot ist gültig bis zum 30. Juni 2026.

    Hinweise
    Installation erfolgt nach Terminabsprache
    Gewährleistung: 12 Monate ab Lieferdatum

    Wir bedanken uns für Ihre Anfrage und freuen uns auf Ihre Rückmeldung.

    Mit freundlichen Grüßen

    Max Mustermann
    TechSolutions GmbH
"""

    
def test_000():
    apa = AnonymousPromptAction(lang="en")
    apa.install()
    new_text = apa._anonymize(TEXT_EN)
    print(new_text)    

def test_010():
    apa = AnonymousPromptAction(lang="de")
    apa.install()
    new_text = apa._anonymize(TEXT_DE)
    print(new_text)
    
def test_020():
    buf = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buf.install()
    buf.push({"values": TEXT_DE})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    buf2 = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buf2.install()
    apa = AnonymousPromptAction(lang="de")
    apa.set_buffer(buf2)
    apa.add_parent(lba)
    apa.install()
    
    apa.execute()
    
    print(apa.get_buffer().data())
    
def test_021():
    buf = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buf.install()
    buf.push({"values": TEXT_EN})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    buf2 = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buf2.install()
    apa = AnonymousPromptAction(lang="en")
    apa.set_buffer(buf2)
    apa.add_parent(lba)
    apa.install()
    
    apa.execute()
    
    print(apa.get_buffer().data())
    