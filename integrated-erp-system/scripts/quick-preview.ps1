# Ensure the output folder exists
$demoFolder = "demo_data"
if (-not (Test-Path $demoFolder)) {
    New-Item -ItemType Directory -Path $demoFolder
}

# Create demo customers
$demoCustomers = @(
    @{ customer_name = "Acme Corporation"; contact = "John Doe"; email = "john@acme.com" },
    @{ customer_name = "TechStart Inc"; contact = "Jane Smith"; email = "jane@techstart.com" },
    @{ customer_name = "Global Solutions Ltd"; contact = "Ali Hassan"; email = "ali@globalsolutions.com" }
)
$demoCustomers | ConvertTo-Json -Depth 3 | Out-File -FilePath "$demoFolder\customers.json" -Encoding UTF8

# Create demo items
$demoItems = @(
    @{ item_code = "LAPTOP-001"; item_name = "Laptop"; price = 1200 },
    @{ item_code = "MOUSE-001"; item_name = "Mouse"; price = 25 },
    @{ item_code = "KEYBOARD-001"; item_name = "Keyboard"; price = 45 }
)
$demoItems | ConvertTo-Json -Depth 3 | Out-File -FilePath "$demoFolder\items.json" -Encoding UTF8

# Create demo maintenance tickets
$demoTickets = @(
    @{ ticket_id = "MT-1001"; customer = "Acme Corporation"; issue = "Laptop not booting"; status = "Open" },
    @{ ticket_id = "MT-1002"; customer = "TechStart Inc"; issue = "Mouse not working"; status = "Closed" },
    @{ ticket_id = "MT-1003"; customer = "Global Solutions Ltd"; issue = "Keyboard keys stuck"; status = "In Progress" }
)
$demoTickets | ConvertTo-Json -Depth 3 | Out-File -FilePath "$demoFolder\tickets.json" -Encoding UTF8