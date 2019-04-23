let sampleColors = [
  '#FF6633',
  '#FFB399',
  '#FF33FF',
  '#FFFF99',
  '#00B3E6',
  '#E6B333',
  '#3366E6',
  '#999966',
  '#99FF99',
  '#B34D4D',
  '#80B300',
  '#809900',
  '#E6B3B3',
  '#6680B3',
  '#66991A',
  '#FF99E6',
  '#CCFF1A',
  '#FF1A66',
  '#E6331A',
  '#33FFCC',
  '#66994D',
  '#B366CC',
  '#4D8000',
  '#B33300',
  '#CC80CC',
  '#66664D',
  '#991AFF',
  '#E666FF',
  '#4DB3FF',
  '#1AB399',
  '#E666B3',
  '#33991A',
  '#CC9999',
  '#B3B31A',
  '#00E680',
  '#4D8066',
  '#809980',
  '#E6FF80',
  '#1AFF33',
  '#999933',
  '#FF3380',
  '#CCCC00',
  '#66E64D',
  '#4D80CC',
  '#9900B3',
  '#E64D66',
  '#4DB380',
  '#FF4D4D',
  '#99E6E6',
  '#6666FF'
]


//get transactions
function getTransactions(){
  let url = window.location.href + "transactions"
  return fetch(url, {
    method:"GET",
    headers:{
      "Content-Type": "application/json"
    }
  })
}

//get current portfolio from transactions
async function getStocks(transactions){
  //convert transactions to a list of totals
  var unappraisedPortfolio = transactions.reduce((accu, curr) => {
    accu[curr.symbol] = accu[curr.symbol] || {
      'count': 0,
      'investment': 0
    };
    accu[curr.symbol].count += (curr.type == "buy" ? parseFloat(curr.count) : -parseFloat(curr.count))
    accu[curr.symbol].investment += (curr.type == "buy" ? parseFloat(curr.cost) : -parseFloat(curr.cost))
    return accu
  },[])
  //for the stocks, get the symbols
  await appraisePortfolio(unappraisedPortfolio)
  return unappraisedPortfolio
}

//get current prices for everything in portfolio
async function appraisePortfolio(portfolio){
  let params = {
    "symbols": Object.keys(portfolio)
  }

  let query = Object.keys(params).map(
    k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k])
  ).join('&');
  //get the iex stats for each symbol
  return fetch("https://cors-anywhere.herokuapp.com/https://ws-api.iextrading.com/1.0/tops/last?" + query, {
    method:"GET",
    headers:{
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest"
    }
  }).then(
    x => x.json()
  ).then(symbols => {
      symbols.map((symbol) => {
        portfolio[symbol.symbol.toLowerCase()]['total'] = (portfolio[symbol.symbol.toLowerCase()].count * symbol.price).toFixed(2)
      })
  })
}

function makeGraph(portfolio){
  var ctx = document.getElementById("pieChart").getContext('2d');
  var labels = Object.keys(portfolio)
  var data = labels.map(label => portfolio[label].total)
  var colors = labels.map((label, i) => sampleColors[i%sampleColors.length])
  labels = labels.map(x => x.toUpperCase())
  var myChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          label: 'Total value',
          data: data,
          backgroundColor: colors
        }],
      },
      options: {
        responsive: false
      }
  });
}

sell = document.querySelector("#sell")
sell.onclick = async function(){
  x = prompt("Which stock would you like to sell?")
  //get the iex stats for each symbol
  await fetch("https://cors-anywhere.herokuapp.com/https://ws-api.iextrading.com/1.0/tops/last?symbols=" + x, {
    method:"GET",
    headers:{
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest"
    }
  }).then(
    res => res.json()
  ).then(
    json => {
      console.log(json)
      return prompt(x + " is going for " + json[0].price + " today. How muck stock would you like to sell?")}
  ).then(
    count => {
      let params = {
        "symbol": x,
        "count": count
      }
      let query = Object.keys(params).map(
        k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k])
      ).join('&');
      fetch("/sell?" + query, {
        method:"POST",
        headers:{
          "Content-Type": "application/json",
        }
      }).then(
        res => res.json()
      ).then(
        res => alert(res.error? res.error: "Success, remaining balance: "+ res.balance)
      )
    })
}

buy = document.querySelector("#buy")
buy.onclick = async function(){
  x = prompt("Which stock would you like to buy?")
  //get the iex stats for each symbol
  await fetch("https://cors-anywhere.herokuapp.com/https://ws-api.iextrading.com/1.0/tops/last?symbols=" + x, {
    method:"GET",
    headers:{
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest"
    }
  }).then(
    res => res.json()
  ).then(
    json => {
      console.log(json)
      return prompt(x + " is going for " + json[0].price + " today. How muck stock would you like to buy?")}
  ).then(
    count => {
      let params = {
        "symbol": x,
        "count": count
      }
      let query = Object.keys(params).map(
        k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k])
      ).join('&');
      fetch("/buy?" + query, {
        method:"POST",
        headers:{
          "Content-Type": "application/json",
        }
      }).then(
        res => res.json()
      ).then(
        res => alert(res.error? res.error: "Success, remaining balance: "+ res.balance)
      )
    })
}

getTransactions().then(
  x => x.json()
).then(
  transactions => {
    var txns = document.querySelector("#transactions")
    txns.innerHTML = "<table><tr><th>Date</th><th>Symbol</th><th>Exchange</th><th>Count</th><th>Cost</th>" +
    transactions.map(x => {
      return '<tr><td>' + new Date(x.purchase_date).toLocaleString() + '</td>' +
              '<td>' + x.symbol.toUpperCase() + '</td>' +
              '<td>' + x.type + '</td>' +
              '<td>' + x.count + '</td>' +
              '<td>' + x.cost + '</td></tr>'
    }).join('') + "</table>"
  return getStocks(transactions)
}).then(
  portfolio => {
    var stats = document.querySelector("#portfolioStats")
    stats.innerHTML = "<table><tr><th>Symbol</th><th>Count</th><th>Investment</th><th>Current Value</th></tr>" +
    Object.entries(portfolio).map((symbol) => {
        return '<tr><td>' + symbol[0].toUpperCase() + '</td>' +
                '<td>' + symbol[1]["count"] + '</td>' +
                '<td>' + symbol[1]["investment"].toFixed(2) + '</td>' +
                '<td>' + symbol[1]["total"] + '</td></tr>'
    }).join('') + "</table>";
    makeGraph(portfolio)
  }
)
