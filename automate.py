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
        self.field_names = (
            'Invoice Number',
            'Invoice Date',
            'Airbill',
            'Bill of Lading',
            'Shipper Account #',
            'Shipper Account Name',
            'Shipper Attention',
            'Shipper Address 1',
            'Shipper Address 2',
            'Shipper City',
            'Shipper State',
            'Shipper ZIP Code',
            'Shipper Reference',
            'Consignee Name',  # Updated to 'to_who'
            'Consignee Attention',
            'Consignee Address 1',
            'Consignee Address 2',
            'Consignee City',
            'Consignee State',
            'Consignee ZIP Code',
            'Consignee Country Code',
            'Third Party Account #',
            'Third Party Account Name',
            'Third Party Address',
            'Third Party Address 2',  # Updated from 'Third Party Address'
            'Third Party City',
            'Third Party State',
            'Third Party ZIP Code',
            'Shipment Date',
            'PO #',
            'Cust Inv #',
            'Dept #',
            'Product Code',
            'Zone',
            'Billed Weight',
            'Actual Weight',
            'Dimensional Weight',
            'Pieces',
            'Dimensions',
            'Base Charge Type',
            'Shipment Total',
            'Base Charge Amount',
            'Charge 1 Type',
            'Charge 1 Amount',
            'Charge 2 Type',
            'Charge 2 Amount',
            'Charge 3 Type',
            'Charge 3 Amount',
            'Charge 4 Type',
            'Charge 4 Amount',
            'Charge 5 Type',
            'Charge 5 Amount'
        )
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

                # Extract charge details from columns
                charges = []
                for i in range(1, 6):
                    old_charge_type = f'Charge {i} Type'
                    old_charge_amt = f'Charge {i} Amount'
                    new_charge_type = row.get(old_charge_type, '')
                    new_charge_amt = row.get(old_charge_amt, '')
                    if new_charge_type and new_charge_amt:
                        charges.append({
                            'name': new_charge_type,
                            'quantity': 1,
                            'unit_cost': float(new_charge_amt)
                        })

                invoice_obj = Invoice(
                    from_who=row['Airbill'],  # Use 'Airbill' as the key
                    to_who=row['Consignee Name'],  # Use 'Consignee Name' as the key
                    logo=self.logo_url,
                    number=row['Invoice Number'],  # Use 'Invoice Number' as the key
                    date=row['Invoice Date'],  # Use 'Invoice Date' as the key
                    due_date='',  # You can fill this in if you have it in your data
                    items=charges,  # Use the extracted charges as items
                    notes=''  # You can fill this in if you have it in your data
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
            invoice_name = f"{invoice.number}_{current_time}_invoice.pdf"  # Unique filename based on timestamp
            invoice_path = os.path.join(self.output_directory, invoice_name)
            with open(invoice_path, 'wb') as f:
                typer.echo(f"Generate invoice for {invoice_name}")
                f.write(pdf)
            typer.echo("File Saved")
        else:
            typer.echo("Fail :", r.text)

def main(csv_name: str = typer.Argument('your_output.csv')):
    # Check if the output directory exists, and if not, create it
    output_directory = 'D:/GitHub/OnlineVIews/InvoiceAutomator/invoices'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    logo_url = 'https://i.ibb.co/ZJLQJmb/selfmade-black.jpg'  # URL of the logo image
    typer.echo(f"Running script with - {csv_name}")
    csv_reader = CSVParser(csv_name, logo_url)
    array_of_invoices = csv_reader.get_array_of_invoices()
    api = ApiConnector(output_directory)
    for invoice in array_of_invoices:
        api.connect_to_api_and_save_invoice_pdf(invoice)

if __name__ == "__main__":
    typer.run(main)
