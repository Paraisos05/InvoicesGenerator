import requests
from dataclasses import dataclass
from typing import List, Dict
import os
import csv
import typer
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

        self.logo_mapping = {
            "esurex": 'https://esurex.com/App_Themes/Standard/images/logo-footer.png',
            "transurit": 'https://transurit.com/App_Themes/Standard/images/logo-header.png',
            "assurem": 'https://assurem.com/App_Themes/Standard/images/logo.png',
            "z2b2": 'https://z2b2.com/wp-content/uploads/2022/01/z2b2-logo-copy-4-1-e1644489368309-300x77.png',
            "default": 'https://www.safetysign.com/images/source/large-images/F4760.png'
        }

    def get_array_of_invoices(self) -> List[Invoice]:
        with open(self.csv_name, 'r') as f:
            reader = csv.DictReader(f, self.field_names)
            invoices_by_user = {}
            header_skipped = False

            for row in reader:
                if not header_skipped:
                    header_skipped = True
                    continue

                full_name = row['FULL_NAME']
                if full_name not in invoices_by_user:
                    invoices_by_user[full_name] = []

                invoices_by_user[full_name].append(row)

            current_csv = []
            for full_name, rows in invoices_by_user.items():
                total_base_charge = 0
                items = []
                processed_airbills = set()

                for row in rows:
                    base_charge = float(row['BASE CHARGE AMOUNT']) if row['BASE CHARGE AMOUNT'] else 0
                    total_base_charge += base_charge

                    airbill_number = row['AIRBILL #']
                    if airbill_number and airbill_number not in processed_airbills:
                        processed_airbills.add(airbill_number)
                        item_name = f"Airbill: {airbill_number}"
                    else:
                        item_name = "Other Charges"

                    for i in range(1, 9):
                        charge_type_key = f"CHARGE {i} TYPE"
                        charge_amt_key = f"CHARGE {i} AMT"
                        charge_type = row[charge_type_key]
                        charge_amt = row[charge_amt_key]

                        if charge_type and charge_amt:
                            charge_amt_float = float(charge_amt)
                            items.append({
                                'name': f"{item_name} - {charge_type}",
                                'quantity': 1,
                                'unit_cost': charge_amt_float
                            })

                if total_base_charge > 0:
                    items.append({
                        'name': 'Total Base Charge Amount',
                        'quantity': 1,
                        'unit_cost': total_base_charge
                    })

                num_unique_airbills = len(processed_airbills)
                reporting_fee = 2.5 * num_unique_airbills
                items.append({
                    'name': 'Reporting fee',
                    'quantity': 1,
                    'unit_cost': reporting_fee
                })

                items.append({
                    'name': 'Insured Value',
                    'quantity': 1,
                    'unit_cost': 0.00
                })

                invoice_obj = Invoice(
                    from_who=f"{rows[0]['FULL_NAME']} \n Email:{rows[0]['EMAIL']}, \n Service:{rows[0]['SCAC']}",
                    to_who=f"{rows[0]['CONSIGNEE ATTENTION']}\n{rows[0]['CONSIGNEE ADDRESS 1']}\n{rows[0]['CONSIGNEE ADDRESS 2']}",
                    logo=self.logo_mapping.get(rows[0]['DATABASE_NAME'].lower(), self.logo_mapping['default']),
                    number=rows[0]['DATABASE_NAME'],
                    date=rows[0]['INVOICE DATE'],
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
            typer.echo(f"Fail: {r.text}")

def main(csv_name: str = typer.Argument('tu_output.csv')):
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
