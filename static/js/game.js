var board_numeric = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, -1, -1, -1, -1, -1, -1, -1, -1, 0,
    0, -1, -1, -1, -1, -1, -1, -1, -1, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]
var isCounterStop = true;
var counter = 30;
const urlObj = new URL(document.URL);
let flask_base_url = urlObj.protocol + '//' + urlObj.hostname;
if (urlObj.port != undefined) {
    flask_base_url = flask_base_url.concat(':' + urlObj.port);
}

async function countDown() {
    if (isCounterStop) {
        counter = 30
        document.getElementById("counter").innerHTML = counter;
        return
    }
    counter--;
    document.getElementById("counter").innerHTML = counter;
    if (counter == 0) { 
        isCounterStop = true;
        alert("Timeout!")
        isEnd = true;
        return 
    }
}
async function init(){
    whitechess_url = document.getElementById("whitechess-image").src;
    blackchess_url = document.getElementById("blackchess-image").src;
    for (var i = 0; i < board_numeric.length; i++) {
        if (board_numeric[i] == -1) {
            document.getElementById("board").rows[Math.floor(i / 10)].cells[i % 10].innerHTML = `<img src=${whitechess_url} width='100%'/>`;
        }
        else if (board_numeric[i] == 1) {
            document.getElementById("board").rows[Math.floor(i / 10)].cells[i % 10].innerHTML = `<img src=${blackchess_url} width='100%'/>`;
        }
    }

    board = document.getElementById("board")
    for (var i = 0; i < board.rows.length; i++) {
        for (var j = 0; j < board.rows[i].cells.length; j++) {
            board.rows[i].cells[j].onclick = async function () {
                r = this.parentElement.rowIndex
                c = this.cellIndex
                handleClick(r,c)
            };
        }
    }
   setInterval(countDown, 1000);

}
var selectX = null;
var selectY = null;
var moving = false;
var isEnd = false;
async function handleClick(row, col) {
    if (moving || isEnd) return

    if (row == selectX - 1 && (col == selectY - 1 || (col == selectY && board_numeric[row*10 + col] != -1) || col == selectY + 1) && board_numeric[row*10 + col] != 1) { 
        isCounterStop = true;
        board = document.getElementById("board")
        document.getElementById("board").rows[row].cells[col].innerHTML = "<img src='static/images/blackchess.png' width='100%'/>"
        document.getElementById("board").rows[selectX].cells[selectY].innerHTML = ""
        document.getElementById("board").rows[selectX].cells[selectY].style = ""
        moving = true;
        board_numeric[selectX * 10 + selectY] = 0
        board_numeric[row * 10 + col] = 1
        document.getElementById("loadinggif").style = " width:50px; height: 50px;  margin:auto;"
        await move(selectX, selectY, row, col)
        document.getElementById("loadinggif").style = "display: none;"
        moving = false;
        selectX = null;
        selectY = null;
        return
    }
    if (selectX != null && selectY != null) { 
        document.getElementById("board").rows[selectX].cells[selectY].style = ""
    }
    if (board_numeric[row * 10 + col] == 1) {
        selectX = row;
        selectY = col;
        document.getElementById("board").rows[row].cells[col].style = "border:3px #FFD382 dashed;";
    }
}


async function move(selectX, selectY, row, col) { 
    if (isEnd) return;
    board = document.getElementById("board")
    let formdata = new FormData();
    formdata.append('move', String.fromCharCode(selectY -1 + 'a'.charCodeAt(0)) + (9-selectX) + String.fromCharCode(col -1 + 'a'.charCodeAt(0)) + (9 - row))
    response = await fetch(`${flask_base_url}/api/play`, {
        method: 'POST',
        body: formdata
    }).then(res => { 
        return res.json()
    })
    console.log(response)
    if (response.status == "move") {
        let original_r = 9 - response['data'][1]
        let original_c = response['data'][0].charCodeAt(0) - 'a'.charCodeAt(0) + 1
        let new_r = 9 - response['data'][3]
        let new_c = response['data'][2].charCodeAt(0) - 'a'.charCodeAt(0) + 1
        board.rows[original_r].cells[original_c].innerHTML = ""
        board.rows[new_r].cells[new_c].innerHTML = "<img src='static/images/whitechess.png' width='100%'/>"
        board_numeric[original_r * 10 + original_c] = 0
        board_numeric[new_r * 10 + new_c] = -1
        isCounterStop = false;
        counter = 30;
        return 
    }
    else if (response.status == "end") {
        if (response.data == 1)
            alert(`The winner is you`);
        else
            alert(`The winner is AI`);
    }
    else if (response.status == "timeout") { 
        alert(`You are too slow`);
    }
    else if (response.status == "error")
    {
        alert(`Error: ${response.data}`);
    }
    isEnd = true;
    return 
    
}