# Import the necessary libraries
from datetime import datetime
import requests
import pandas as pd
import os
import re
import subprocess
terminal_width = os.get_terminal_size().columns

# Prints started header
print('-' * terminal_width)
print(f'Start: {datetime.now()}')
print('-' * terminal_width)

# Set the website URL
url = "https://www.cloudping.cloud/endpoints"

# Prints url o perform request
print(f"Performing server requests in {url}")
print('-' * terminal_width)

# Make a GET request to obtain the site's HTML content
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Prints processing started
    print("Starting site table processing...")
    print('-' * terminal_width)

    # Extract HTML table using pandas
    table = pd.read_html(response.text)[0]

    # Get the "Cloud" "Ping Hostname" and "Region" columns
    column_cloud = table["Cloud"]
    column_hostname = table["Ping Hostname"]
    column_region = table["Region"]

    # Remove the "copy" value and trim each element in the "Ping Hostname" column
    column_hostname = column_hostname.str.lower().str.replace("copy", "").str.strip()

    # Create a list to store card data
    card_list = []

    # Create a variable to count how many records were successfully tested
    success_count = 0

    # Create a variable to count how many records had an error
    error_count = 0

    # Run a "ping" command using each element in the "Ping Hostname" column as an argument
    for i in range(len(column_hostname)):
        cloud = column_cloud[i]
        hostname = column_hostname[i]
        region = column_region[i]

        # Use the subprocess module to run the ping command and capture the output
        output = subprocess.run(["ping", "-n", "1", hostname], capture_output=True, text=True)

        # Check if the command was successful
        if output.returncode == 0:
            # Extract the ping value in ms from the output using another regular expression
            match = re.search(r"(tempo|time)=(\d+\.?\d*) ?(ms|milissegundos)", output.stdout)
            if match:
                value = int(match.group(2))

                # Create a dictionary with cloud, region, hostname and ping
                card_data = {"cloud": cloud, "region": region, "hostname": hostname, "ping": value}

                # Prints the card data
                print(card_data)

                # Add dictionary to card list
                card_list.append(card_data)

                # Increment the success counter
                success_count += 1
        else:
            # Increment the error counter
            error_count += 1

    # Sort the card list by ping value in ascending order
    card_list.sort(key=lambda x: x["ping"])

    # Count how many objects have ping less than 100
    count_100 = len(list(filter(lambda x: x["ping"] <= 100, card_list)))

    # Count how many objects have ping less than 150
    count_150 = len(list(filter(lambda x: x["ping"] >= 100 and  x["ping"]<= 150, card_list)))

    # Count how many objects have ping greater than 150
    count_m150 = len(list(filter(lambda x: x["ping"] > 150, card_list)))

    # Total items in card list
    count_total = len(card_list)

    # Percentage that have ping less than 100 relative to the total
    count_100_percent = (count_100 * 100) / count_total

    # Percentage that have ping less than 150 relative to the total
    count_150_percent = (count_150 * 100) / count_total

    # Percentage that have a ping greater than 150 relative to the total
    count_m150_percent = (count_m150 * 100) / count_total

    # Creating html file header
    html_head = """<!doctype html>
    <html lang="pt-br"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"> <!-- Bootstrap CSS --> <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous"><title>Cloud Ping Report</title> <style>.card-body.text-success {background-color:#dcf9eb}.card-body.text-warning {background-color:#f9ebdc}.card-body.text-danger {background-color:#f9dcea}   </style></head> <body> """

    # Creating html file footer
    html_foot = """<script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js" integrity="sha384-oBqDVmMz9ATKxIep9tiCxS/Z9fNfEXiDAYTujMAeBAsjFuCZSmKbSSUnQlmh/jp3" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.min.js" integrity="sha384-cuYeSxntonz0PPNlHhBs68uyIAVpIIOZZ5JqeqvYYIcEL727kskC66kF92t6Xl2V" crossorigin="anonymous"></script></body> </html> """


    # Creating a container in HTML for the cards
    html_container = f"""<div class="container">
    <div class="card text-bg-dark" style="width: 100%;margin: 20px 0 20px 0 ;">
    <div class="card-body">
        <h5 class="card-title">Cloud Ping Report</h5>
        <h6 class="card-subtitle mb-2 text-muted">Ping testing result for cloud servers</h6>
        <p class="card-text">
            <strong>Servers</strong> {len(column_hostname)}, <strong>Pings</strong> {success_count}, <strong>Errors</strong> {error_count}
        </p>
    </div>
    </div>
    <div class="card-body text-success" style="width: {count_100_percent}%;margin: 2px 0 0 0;padding: 0 0 0 10px"><100&emsp;({count_100})</div>
    <div class="card-body text-warning" style="width: {count_150_percent}%;margin: 2px 0 0 0;padding: 0 0 0 10px"><150&emsp;({count_150})</div>
    <div class="card-body text-danger" style="width: {count_m150_percent}%;margin: 2px 0 0 0;padding: 0 0 0 10px">+150&emsp;({count_m150})</div>
    <br/>
    <div class="row row-cols-1 row-cols-md-3 g-4"> """

    # Create an HTML template for each card using f-strings to dynamically insert data
    html_card_template = """<div class="col">
    <div class="card">
    <div class="card-body text-{status}">
    <h5 class="card-title text-{status}">{ping}ms</h5>
    <h6 class="card-subtitle text-muted">{cloud}, {region}</h6>
    <p class="card-text text-muted">{hostname}</p>
    </div>
    </div>
    </div> """

    # Create an empty list to store cards in HTML
    html_card_list = []

    # Iterate over the list of cards and apply the HTML template to each one
    for card in card_list:
        cp = card['ping']

        # Setting the color by ping range
        if cp <= 100:
            card["status"] = "success"
        elif cp <=150:
            card["status"] = "warning"
        else:
            card["status"] = "danger"

        html_card = html_card_template.format(**card)
        html_card_list.append(html_card)

    # Join HTML cards into a single string
    html_cards = "".join(html_card_list)

    # Close the HTML container
    html_container_end = """</div></div> """

    # Concatenate HTML parts into a single string
    html_report = html_head + html_container + html_cards + html_container_end + html_foot

    # Save the HTML string to a file in current directory
    with open("cloudping-report.html", "w") as f:
        f.write(html_report)

    # Print a success message
    print("Report successfully generated in the same directory with name cloudping-report.html")

else:
    # Report that there was an error in the request
    print(f"Erro ao acessar o site: {response.status_code}")