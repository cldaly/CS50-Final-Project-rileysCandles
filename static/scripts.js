// Function to calculate the total cost of sale while on buy.html or restock.html page
function confirmPrice() {
    // Lookup the number of units user is looking to buy
    var qty = document.getElementById("qty_select").value;
    qty_int = parseInt(qty, 10);

    // Lookup the price of one candle user has selected to buy
    var price = document.getElementById("price_calc").innerHTML;
    price_float = parseFloat(price.replace('$', ''));
    // Turn quantity from string to int

    // Calculate total cost, and round to 2 decimal places
    var total_cost = qty_int * price_float;
    total_cost = total_cost.toFixed(2)

    // Insert text with total cost into calc_output element
    document.getElementById("calc_output").innerHTML = "$" + total_cost;

    // Lookup the account balance of user
    balance = document.getElementById("balance_calc").innerHTML;
    balance = +(balance.match(/\d+[,\.]?\d+/)[0].replace(",","."));
    balance = parseFloat(balance.toFixed(2));

    // Change color of the cost calculation if user does not have enough money
    if (parseFloat(total_cost) > balance) {
        document.getElementById("calc_output").style.color = "#b73e3e";
    } else {
        document.getElementById("calc_output").style.color = "#3eb75a";
    }
}

// Function used to calculate total cost to add new candles to inventory
function confirmNewPrice() {
    // Look up number of units user is looking to add
    var qtyNew = document.getElementById("qty_select_new").value;
    qtyNew = parseInt(qtyNew, 10);

    // Lookup the cost user has given to unit
    var cost = document.getElementById("cost").value;
    cost = parseFloat(cost);

    // Calculate total cost to add candle to inventory
    var total_cost = qtyNew * cost;
    total_cost = total_cost.toFixed(2);

    // Insert text with total cost into calc_output_new element
    document.getElementById("calc_output_new").innerHTML = "$" + total_cost;

    // Lookup the account balance of user
    balanceNew = document.getElementById("balance_calc_new").innerHTML;
    balanceNew = +(balanceNew.match(/\d+[,\.]?\d+/)[0].replace(",","."));
    balanceNew = parseFloat(balanceNew.toFixed(2));

    // Change color of the cost calculation if user does not have enough money
    if (parseFloat(total_cost) > balanceNew) {
        document.getElementById("calc_output_new").style.color = "#b73e3e";
    } else {
        document.getElementById("calc_output_new").style.color = "#3eb75a";
    }
}

// This function will be used in conjunction with confirmNewPrice()
// This will be used to disable selecting quantity until a cost has been added
function newCost() {
    // Lookup cost added by user
    var costCheck = document.getElementById("cost").value;

    // If no cost has been added, disable qty selctor, change output
    if (costCheck == "") {
        document.getElementById("qty_select_new").disabled=true;
        document.getElementById("calc_output_new").innerHTML = "Please enter a cost";
        document.getElementById("calc_output_new").style.color = "#999";
    } else {
        // If value has been added, enable selector
        document.getElementById("qty_select_new").disabled=false;
        var qtyCheck = document.getElementById("qty_select_new").value;

        // Run confirmNewPrice() if quantity has been selected
        if (qtyCheck != "Blank") {
            confirmNewPrice();
        }
    }
}