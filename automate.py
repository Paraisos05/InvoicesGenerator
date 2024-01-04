import requests
from dataclasses import dataclass
from typing import List
import os
import csv
import typer
import json
from datetime import datetime

@dataclass
class Invoice:
    from_who: str
    to_who: str
    logo: str
    number: str
    date: str
    due_date: str
    items: List[dict]
    notes: str

class CSVParser:
    def __init__(self, csv_name: str, logo_url: str) -> None:
        self.field_names = [
            "INVOICE #",
            "INVOICE DATE",
            "AIRBILL #",
            "BILL OF LADING",
            "SHIPPER ACCOUNT #",
            "SHIPPER ACCOUNT NAME",
            "SHIPPER ATTENTION",
            "SHIPPER ADDRESS 1",
            "SHIPPER ADDRESS 2",
            "SHIPPER CITY",
            "SHIPPER STATE",
            "SHIPPER ZIP CODE",
            "SHIPPER REFERENCE",
            "CONSIGNEE NAME",
            "CONSIGNEE ATTENTION",
            "CONSIGNEE ADDRESS 1",
            "CONSIGNEE ADDRESS 2",
            "CONSIGNEE CITY",
            "CONSIGNEE STATE",
            "CONSIGNEE ZIP CODE",
            "CONSIGNEE COUNTRY CODE",
            "THIRD PARTY ACCOUNT #",
            "THIRD PARTY ACCOUNT NAME",
            "THIRD PARTY ADDRESS",
            "THIRD PARTY ADDRESS.1",
            "THIRD PARTY CITY",
            "THIRD PARTY STATE",
            "THIRD PARTY ZIP CODE",
            "SHIPMENT DATE",
            "PO #",
            "CUST INV #",
            "DEPT #",
            "PRODUCT CODE",
            "ZONE",
            "BILLED WEIGHT",
            "ACTUAL WEIGHT",
            "DIMENSIONAL WEIGHT",
            "PIECES",
            "DIMENSIONS",
            "BASE CHARGE TYPE",
            "SHIPMENT TOTAL",
            "BASE CHARGE AMOUNT",
            "CHARGE 1 TYPE",
            "CHARGE 1 AMT",
            "CHARGE 2 TYPE",
            "CHARGE 2 AMT",
            "CHARGE 3 TYPE",
            "CHARGE 3 AMT",
            "CHARGE 4 TYPE",
            "CHARGE 4 AMT",
            "CHARGE 5 TYPE",
            "CHARGE 5 AMT",
            "CHARGE 6 TYPE",
            "CHARGE 6 AMT",
            "CHARGE 7 TYPE",
            "CHARGE 7 AMT",
            "CHARGE 8 TYPE",
            "CHARGE 8 AMT",
            "CREDIT 1 DESCRIPTION",
            "CREDIT 1 AMT",
            "CREDIT 2 DESCRIPTION",
            "CREDIT 2 AMT",
            "CREDIT 3 DESCRIPTION",
            "CREDIT 3 AMT",
            "REFERENCE 2",
            "REFERENCE 3",
            "REFERENCE 4",
            "REFERENCE 5",
            "CUSTOMERID",
            "SCAC",
            "CLASS",
            "CHARGENOTES",
            "RECEIVEDBY",
            "RECEIVEDATE",
            "FULL_NAME",
            "EMAIL",
            "DATABASE_NAME"
        ]
        self.csv_name = csv_name
        self.logo_url = logo_url

    def get_array_of_invoices(self) -> List[Invoice]:
        with open(self.csv_name, 'r') as f:
            reader = csv.DictReader(f, self.field_names)
            current_csv = []
            header_skipped = False  # Flag to skip the header row
            for row in reader:
                if not header_skipped:
                    header_skipped = True
                    continue  # Skip the header row

                # Initialize an empty items list for each invoice
                items = []

                # Define the columns for charge types and amounts
                charge_columns = [
                    ("CHARGE 1 TYPE", "CHARGE 1 AMT"),
                    ("CHARGE 2 TYPE", "CHARGE 2 AMT"),
                    ("CHARGE 3 TYPE", "CHARGE 3 AMT"),
                    ("CHARGE 4 TYPE", "CHARGE 4 AMT"),
                    ("CHARGE 5 TYPE", "CHARGE 5 AMT"),
                    ("CHARGE 6 TYPE", "CHARGE 6 AMT"),
                    ("CHARGE 7 TYPE", "CHARGE 7 AMT"),
                    ("CHARGE 8 TYPE", "CHARGE 8 AMT")
                ]

                # Iterate through charge columns to extract charges
                for charge_type_column, charge_amt_column in charge_columns:
                    charge_type = row[charge_type_column]
                    charge_amt = row[charge_amt_column]

                    if charge_type and charge_amt:
                        # Rename "Additional Handling - Length+Girth" to "Additional Surcharges"
                        if charge_type == "Additional Handling - Length+Girth":
                            charge_type = "Additional Surcharges"

                        # Add charge item with the extracted charge type and amount
                        items.append({
                            'name': charge_type,
                            'quantity': 1,
                            'unit_cost': float(charge_amt)
                        })

                # Add the Weight item using "BILLED WEIGHT" if it's not empty
                billed_weight_str = row['BILLED WEIGHT']
                if billed_weight_str:
                    billed_weight = float(billed_weight_str)
                    items.append({
                        'name': 'Weight',
                        'quantity': 1,
                        'unit_cost': billed_weight
                    })

                # Add the Base Transportation item
                base_charge_amount_str = row['BASE CHARGE AMOUNT']
                if base_charge_amount_str:
                    base_charge_amount = float(base_charge_amount_str)
                    items.append({
                        'name': 'Base Transportation',
                        'quantity': 1,
                        'unit_cost': base_charge_amount
                    })

                # Add the "Reporting fee $ 2.50" item
                items.append({
                    'name': 'Reporting fee',
                    'quantity': 1,
                    'unit_cost': 2.50
                })

                invoice_obj = Invoice(
                    from_who=row['FULL_NAME'],
                    to_who=row['CONSIGNEE NAME'],
                    logo=self.logo_url,
                    number=row['SHIPPER REFERENCE'],
                    date=row['INVOICE DATE'],
                    due_date='',
                    items=items,
                    notes=''
                )
                current_csv.append(invoice_obj)
        return current_csv

class ApiConnector:
    def __init__(self, output_directory: str) -> None:
        self.headers = {"Content-Type": "application/json"}
        self.url = 'https://invoice-generator.com'
        self.output_directory = output_directory

    def connect_to_api_and_save_invoice_pdf(self, invoice: Invoice) -> None:
        invoice_parsed = {
            'from': invoice.from_who,
            'to': invoice.to_who,
            'logo': invoice.logo,
            'number': invoice.number,
            'date': invoice.date,
            'due_date': invoice.due_date,
            'items': invoice.items,
            'notes': invoice.notes
        }
        r = requests.post(self.url, json=invoice_parsed, headers=self.headers)
        if r.status_code == 200 or r.status_code == 201:
            pdf = r.content
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            invoice_name = f"{invoice.number}_{current_time}_invoice.pdf"
            invoice_path = os.path.join(self.output_directory, invoice_name)
            with open(invoice_path, 'wb') as f:
                typer.echo(f"Generate invoice for {invoice_name}")
                f.write(pdf)
            typer.echo("File Saved")
        else:
            typer.echo("Fail :", r.text)

def main(csv_name: str = typer.Argument('your_output.csv')):
    output_directory = 'D:\GitHub\Freelancer\InvoicesGenerator\invoices'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    logo_url = 'https://www.safetysign.com/images/source/large-images/F4760.png'
    typer.echo(f"Running script with - {csv_name}")
    csv_reader = CSVParser(csv_name, logo_url)
    array_of_invoices = csv_reader.get_array_of_invoices()
    api = ApiConnector(output_directory)
    for invoice in array_of_invoices:
        api.connect_to_api_and_save_invoice_pdf(invoice)

if __name__ == "__main__":
    typer.run(main)
