window.addEventListener('load', () => {
    var socket = io();
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });
    
    socket.emit('join')
    //最初に自分の名前を二回受け取らないための真偽値
    let firstname = true

    const canvas = document.querySelector('#draw-area');
    const context = canvas.getContext('2d');

    const lastPosition = { x: null, y: null };
    let isDrag = false;
    let isPen = true;
    
    //自分の番かどうか判別する真偽値
    let isWriter = false;

    // 現在の線の色を保持する変数(デフォルトは黒(#000000)とする)
    let currentColor = '#000000';

    //何か書き込みをしたかの真偽値 falseだと送信ができない
    let waswrote = false;
    
    
    context.fillStyle = 'rgb(256, 256, 256)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    

    function draw(x, y) {
      if(!isDrag) {
        return;
      }
      if(!waswrote && isPen){
        waswrote=true;
      }
      context.lineCap = 'round';
      context.lineJoin = 'round';
      context.lineWidth = 5;
      context.strokeStyle = currentColor;
      if (lastPosition.x === null || lastPosition.y === null) {
        context.moveTo(x, y);
      } else {
        context.moveTo(lastPosition.x, lastPosition.y);
      }
      context.lineTo(x, y);
      context.stroke();
  
      lastPosition.x = x;
      lastPosition.y = y;
      if(isWriter){
        socket.emit('client_to_server',lastPosition);
      }
    }
  
    function clear(nowis) {
      console.log(nowis);
      if(nowis == true){
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.fillStyle = 'rgb(256, 256, 256)';
        context.fillRect(0, 0, canvas.width, canvas.height);
      }
      waswrote = false;
    }
  
    function dragStart(event) {
      console.log('dragstart');
      context.beginPath();
      isDrag = true;
      if(isWriter){
        socket.emit('drag_start_client');
      }
    }
  
    function dragEnd(event) {
      context.closePath();
      isDrag = false;
      lastPosition.x = null;
      lastPosition.y = null;
      if(isWriter){
        socket.emit('drag_end_client');
      }
    }

    function eraser(){
      if (isPen == true){
        currentColor = '#FFFFFF';
        isPen = false;
        document.getElementById("eraser-button").innerHTML = "ペンモード";
      }
      else{
        currentColor = '#000000';
        isPen = true;
        document.getElementById("eraser-button").innerHTML = "消しゴムモード";
      }
    }

    function sendServer(url, param){
      fetch(url, param);
    }
    
    const pic_send_URL = "/pic";

    function initEventHandler() {
      const clearButton = document.querySelector('#clear-button');
      clearButton.addEventListener('click', function(){
        console.log("infunction");
        clear(isWriter);
        if(isWriter){
          console.log("inif");
          socket.emit('clear_button');
          waswrote = false;
        }
      });
  
      // 消しゴムモードを選択したときの挙動
      const eraserButton = document.querySelector('#eraser-button');
      eraserButton.addEventListener('click',function(){
        if(isWriter){
          socket.emit('eraser_button');
          eraser;
        }
      });
  
      const endButton = document.querySelector('#end-button');
      endButton.addEventListener('click', function(){
        // Canvasのデータを取得
        if(isWriter){
          if(waswrote){

            var board = document.getElementById('draw-area');
            const dateURL = board.toDataURL("image/png");  // DataURI Schemaが返却される
        
            // 送信情報の設定
            const param  = {
              method: "POST",
              headers: {
                "Content-Type": "application/json; charset=utf-8"
              },
            body: JSON.stringify({date: dateURL})
            }
            // サーバへ送信
            sendServer(pic_send_URL, param);
            socket.emit('end_button');
            isWriter = false;
          }
          else{
            alert("絵を書いてください。")
          };
        };
      });

      // const leaveButton =document.querySelector('#leave');
      // leaveButton.addEventListener('click', function(){
      //     socket.emit("leave");
      // });
  
      canvas.addEventListener('mousedown', dragStart);
      canvas.addEventListener('mouseup', dragEnd);
      canvas.addEventListener('mouseout', dragEnd);
      canvas.addEventListener('mousemove', (event) => {
        if(isWriter){
          draw(event.layerX, event.layerY);
        }
      });
    }
  
    socket.on('server_to_client', function(msg) {
      if(!isWriter){
        isDrag = true;
        draw(msg['x'],msg['y']);
        isDrag =false;
      }
    });
    
    socket.on('server_clear_button', function(){
      console.log("recive_clear button")
      clear(true);
    });

    socket.on('drag_end_server', function(){
      context.beginPath();
      isDrag = true;
    });

    socket.on('drag_end_server', function(){
      context.closePath();
      isDrag = false;
      lastPosition.x = null;
      lastPosition.y = null;
    });

    socket.on('server_eraser',eraser);

    socket.on('server_pic', function(msg) {
      const divEl = document.createElement("div");
      const divChildEl = document.createElement("div");
      divChildEl.setAttribute("class", "name");
      divChildEl.textContent = msg['user_name'];
      const imgEl = document.createElement("img");
      imgEl.setAttribute("class", "log");
      imgEl.src = `static/pic/${msg['file_name']}`;
      imgEl.alt = msg['user_name'];
      divEl.appendChild(divChildEl);
      divEl.appendChild(imgEl);

      const logbox = document.querySelector("#log_box");
      logbox.appendChild(divEl);
    });

    socket.on('select_writer', function(){
      isWriter = true;
      clear(true);
    });

    socket.on('who_writer', function(message){
      document.getElementById("now_writer").innerHTML = message;
    });

    socket.on('after_join', function(date) {
      if (firstname == false){
        const liEl = document.createElement("li");
        liEl.textContent = date;
        liEl.id = date;
        liEl.className = "name"
        console.log(`name ${date}`);
        const ulEl = document.querySelector("#player");
        ulEl.appendChild(liEl);
      }
      else{
        firstname = false;
      }   
    });
    
    socket.on('after_leave', function(date) {
      const removeEl = document.getElementById(date);
      removeEl.remove();
    });

    initEventHandler();
    
});

