const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let html_alarmen;
let html_smartlamp;
let html_statuslamp;
let chart;
let ctx;
let btnPower;

const listenToUI = function () {
  ctx = document.getElementById('tempChart').getContext('2d');
  btnPower = document.getElementById('btnPower');
  btnPower.addEventListener("click",shutdown)
  chart = new Chart(ctx);
  html_statuslamp = document.querySelector(".js-status-lamp");
  html_smartlamp = document.querySelector(".js-smart-light-bg");
  html_smartlamp.addEventListener("click", changeStatusLamp);

};

const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });

  socket.on("B2F_temperatuur", function (jsonObject) {
    console.log("Dit is de status van de temperatuur");
    console.log(jsonObject);
    let testje = document.querySelector('.js-temperatuur');
    let temper = `${jsonObject.meting} °C`;
    testje.innerHTML = temper;
  });

  socket.on("B2F_grafiek", function (jsonObject) {
    console.log("Temperatuur grafiek");
    console.log(jsonObject);
    chart.destroy()
    let labels =[], data = [];
    for (const element of jsonObject) {
      labels.push(element.datum);
      data.push(element.meting)
    }
    chart = new Chart(ctx, {
      // The type of chart we want to create
      type: 'line',
  
      // The data for our dataset
      data: {
          labels: labels,
          datasets: [{
              label: 'Temperatuur',
              backgroundColor: 'rgba(0, 0, 0, 0)',
              borderColor: 'rgb(241, 106, 56)',
              lineTension: 0,              
              data: data,
              pointBackgroundColor: "rgb(241, 106, 56)",
              pointBorderColor: "rgb(241, 106, 56)",
              pointHoverBackgroundColor: "rgb(241, 106, 56)",
              pointHoverBorderColor: "rgb(241, 106, 56)",
              pointRadius: 0,
              pointHoverRadius: 4,            
          }]
      },
  
      // Configuration options go here
      options: {
      }
    });
  });

  socket.on("B2F_statusLamp", function(jsonObject) {
    console.log(jsonObject);
    if(jsonObject.status == 'statisch') {
      html_smartlamp.style.backgroundColor = jsonObject.kleur;
    }
    else if (jsonObject.status == 'uit'){
      html_smartlamp.style.backgroundColor = "#FFFFFF";
    }
    else if (jsonObject.status == 'kleur'){
      html_smartlamp.style.backgroundColor = "#F16A38";
    }
    html_statuslamp.innerHTML = `<h2 class="">${jsonObject.status}</h2>`;
    //To do statuslamp aanpassen
  });
};
//#region ***  Callbacks***
const callbackAlarmen = function(jsonObject) {
  let htmlstring = "";
  console.log(jsonObject);
  for (const element of jsonObject) {
    console.log(element);
    let knop;
    if(element.status == 1) {
      knop = "Aan";
    }
    else {
      knop = "Uit";
    }
    ///Dageb moeten hier niet in oranje, is enkel bij bewerken.
    let dagen = ["Man", "Din", "Woe","Don","Vrij","Zat","Zon"];
    let herhaling = element.herhaling;
    let dagHtml = "";
    for (var i = 0; i < herhaling.length; i++) {
      let aan = herhaling.charAt(i);
      if(aan == "1") {
        dagHtml += `<li class="">${dagen[i]}</li>`;
      }
    }
    
    let link = "/alarmen.html?alarmID="+element.idAlarm;
    htmlstring += `
    <div style='background-color: ${element.kleur}' class='c-alarm u-1-of-2-bp2 o-layout__item'>
      <div class='o-layout  o-layout--align-center c-alarm-inner'> 
        <div class='o-layout__item u-3-of-5'>
          <h5>${element.titel}</h5>
          <h1>${element.tijdstip}</h1>
          <ul> 
            ${dagHtml}
          </ul>
        </div>
        <div class='o-layout o-layout--align-center o-layout__item u-2-of-5'>
          <div class=' o-layout__item  u-1-of-2'>
            <div class='c-alarm-btn'>
              <p href="" class="js-on-off" data-alarm-id="${element.idAlarm}">${knop}</p>  
            </div>
          </div>
          <div class='o-layout__item u-1-of-2'>
            <a href='${link}'><img src="/img/btn.svg"></a>    
          </div>   
        </div>  
      </div>
    </div>`;

  }
  html_alarmen.innerHTML = htmlstring;
  listenToClickOnOff();  
};
//#endregion

//#region ***  Clicks  ***
const shutdown = function() {
  socket.emit("F2B_shutdown");
}

const listenToClickOnOff = function() {
  const knoppen = document.querySelectorAll(".js-on-off");
  for (const knop of knoppen) {
          let body = null;
          knop.addEventListener("click", function() {
          const id = knop.getAttribute("data-alarm-id");
          console.log(id);
          if(knop.innerHTML =="Aan") {
            body = JSON.stringify({
              value: false
            })
            knop.innerHTML = `Uit`;
          }
          else {
            body = JSON.stringify({
              value: true
            })
            knop.innerHTML = `Aan`;
          }
          
          updateOnOffAlarm(id,body);
      });
  }
};

const changeStatusLamp = function() {
  html_smartlamp.style.backgroundColor = "#ffffff";
  html_statuslamp.innerHTML = `<h2 class="">Uit</h2>`;  
  updateOnOffLamp(1);
};

//#region ***  Data Access - get___ ***
const getAlarms = function() {
  handleData(`http://169.254.10.1:5000/api/alarmen`, callbackAlarmen);
};
const updateOnOffAlarm = function(id,body) {
  handleData(`http://169.254.10.1:5000/api/alarmen/changeOnOff/${id}`,console.log, console.log,["PUT"],body);
};
const updateOnOffLamp = function(wekkerID) {
  handleData(`http://169.254.10.1:5000/api/smartlamp/changeOnOff/${wekkerID}`,console.log, console.log,["PUT"]);  
};
//#endregion
document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  html_alarmen = document.querySelector(".js-alarmen");
  listenToUI();
  listenToSocket();
  getAlarms();
});
