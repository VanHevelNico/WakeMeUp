const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let html_muziekjes;
let html_kleur;
let html_week;

//Vars muziek selectie
let btnCheck = 0;
let vorigeBtn = "";
let vorigeBtnInner = "";
let bestandMuziek = null;
let alarmID = null;
let update = 0;
let btnPower;

const listenToUI = function () {
  html_muziekjes = document.querySelector(".js-muziekje");
  //Kleuren toevegen aan de dropdown
  html_kleur = document.querySelector(".js-kleur");
  let kleur = ["gewoon", "flikker", "kleur"];
  let kleurnaam = ["Zonlicht simulatie","Flikkerend licht", "Kleurenwiel"]
  let htmlstring = ``;
  for(let i = 0; i < 3;i++) {
    htmlstring += `<option value="${kleur[i]}">${kleurnaam[i]}</option>`;
  }
  html_kleur.innerHTML = htmlstring;
  //Weekdagen tonenen
  html_week = document.querySelector(".js-alarm-week");
  let week = ["Man","Din","Woe","Don","Vrij","Zat","Zon"];
  htmlstring = ``;
  for(let i = 0; i < 7; i++) {
    htmlstring += `<li><p style="background-color: rgb(255, 255, 255); color: rgb(0, 0, 0);" class='js-dag-btn c-dag-btn' data-aanUit='0' data-weekdag='${week[i]}'>${week[i]}</p></li>`;
  }
  html_week.innerHTML = htmlstring;
  listenToClickDag();
  const urlParams = new URLSearchParams(window.location.search);
  alarmID = urlParams.get('alarmID');
  if(alarmID != null) {
    getAlarmID(1,alarmID);
    update = 1;
    let titel = document.getElementById('js-alarm-titel');
    titel.innerHTML = `Bewerk alarm`;
    let div = document.querySelector('.js-add-alarm-div');
    let htmlstring = `
    <ul class='c-btn-list'>
    <li class="js-add-alarm c-btn" id="js-add-alarm" ><h3><img src='/img/save.svg'></h3></li>
    <li id="" class="c-btn js-delete-alarm"><h3><img src='/img/delete.svg'></h3></li>
    </ul>
    `;
    div.innerHTML = htmlstring;
    luisterNaarClickDelete();
  }
  console.log(alarmID);
  getMuziekjes();
  btnPower = document.getElementById('btnPower');
  btnPower.addEventListener("click",shutdown);
  luisterNaarClickAdd();
};

//#region ***  Callbacks***
const callbackMuziekjes = function(jsonObject) {
    let htmlstring = "";
    console.log(jsonObject);
    for (const element of jsonObject) {
        console.log(element);          
        let artiest = "";
        if(element.Artiest != null) {
          artiest = element.Artiest;
        }
        htmlstring += `
          <div class='c-muziekje u-1-of-4 u-1-of-6-bp2'>
            <div data-muziek-id='${element.FileNaam}' class='c-muziekje-btn js-muziek-btn'>
              <div class='c-muziekje-btn--inner js-muziek-btn--inner'>
                <img src="/img/muziek.svg">
              </div>
            </div>
            <h4>${element.Titel}</h4>
            <p>${artiest}</p>
          </div>
        `;
    }
    html_muziekjes.innerHTML = htmlstring;
    listenToClickMuziekje();     
};

const callbackBewerken = function(jsonObject) {
  console.log(jsonObject);
  //Uur aanpassen
  let uur_input = document.getElementById("js-uur");
  uur_input.value = jsonObject.tijdstip;
  //Knoppen week
  const buttons  = document.querySelectorAll(".js-dag-btn");
  let teller = 0;
  for(const btn of buttons) {
    let herhaling = jsonObject.herhaling[teller];
    if(herhaling == "1") {
      btn.style.backgroundColor = "#F16A38";
      btn.style.color = "#FFFFFF";
      btn.setAttribute("data-aanUit","1")     
    }
    else {
      btn.style.backgroundColor = "#FFFFFF";
      btn.style.color = "#000000";   
      btn.setAttribute("data-aanUit","0")     
    }
    teller += 1;
  }
  //Titel
  let titel = document.getElementById("js-titel");
  titel.value = jsonObject.titel;
  //Deuntjes
  const liedjes  = document.querySelectorAll(".js-muziek-btn");
  for(const liedje of liedjes) {
    let deuntje = jsonObject.deuntje;
    if(deuntje == liedje.getAttribute('data-muziek-id')) {
     //Vorige btns uitzetten
      if(btnCheck == 1) {
        vorigeBtn.style.backgroundColor = "#F16A38";
        vorigeBtnInner.style.backgroundColor = "#BF542C";
      }
      else {
        btnCheck = 1
      }
      liedje.style.backgroundColor  = "#38F1A6";
      let btnInner = liedje.querySelector(".js-muziek-btn--inner");
      btnInner.style.backgroundColor = "#32D995";
      vorigeBtn = liedje;
      vorigeBtnInner = btnInner;
      bestandMuziek = liedje.getAttribute("data-muziek-id"); 
    }
    else {
      //Anders niets doen
    }
  }
  console.log("We zijn hier geraakt");
  let kleur = ["uit","gewoon", "flikker", "kleur"];
  let kleurnaam = ["Uit","Zonlicht simulatie","Flikkerend licht", "Kleurenwiel"]
  let htmlstring = ``;
  let lichteffect = jsonObject.lichteffect;
  console.log(lichteffect);
  for(let i = 0; i < 4;i++) {
    if(lichteffect == kleur[i]) {
      htmlstring += `<option value="${kleur[i]}" selected>${kleurnaam[i]}</option>`;
    }
    else {
      htmlstring += `<option value="${kleur[i]}">${kleurnaam[i]}</option>`;
    }  
  }
  html_kleur.innerHTML = htmlstring;
  //kleur input 
  let kleurInput = document.getElementById("js-kleur-2");
  kleurInput.value = jsonObject.kleur;  
}
//#endregion

//#region ***  Clicks  ***
const shutdown = function() {
  socket.emit("F2B_shutdown");
}

const listenToClickDag = function() {
  const buttons  = document.querySelectorAll(".js-dag-btn");
  for(const btn of buttons) {
    btn.addEventListener("click",function() {
      if(btn.getAttribute("data-aanUit") == "0") {
        btn.style.backgroundColor = "#F16A38";
        btn.style.color = "#FFFFFF";
        btn.setAttribute("data-aanUit","1")     
      }
      else {
        btn.style.backgroundColor = "#FFFFFF";
        btn.style.color = "#000000";   
        btn.setAttribute("data-aanUit","0")     
      }

    });
  }
}

const listenToClickMuziekje = function() {
  const buttons  = document.querySelectorAll(".js-muziek-btn");
  for(const btn of buttons) {
    btn.addEventListener("click",function() {
      //Vorige btns uitzetten
      if(btnCheck == 1) {
        vorigeBtn.style.backgroundColor = "#F16A38";
        vorigeBtnInner.style.backgroundColor = "#BF542C";
      }
      else {
        btnCheck = 1
      }
      //Huidige btns activeren
      btn.style.backgroundColor  = "#38F1A6";
      let btnInner = btn.querySelector(".js-muziek-btn--inner");
      btnInner.style.backgroundColor = "#32D995";
      vorigeBtn = btn;
      vorigeBtnInner = btnInner;
      bestandMuziek = btn.getAttribute("data-muziek-id");
    });
  }  
}

const luisterNaarClickDelete = function() {
  document.querySelector(".js-delete-alarm").addEventListener("click",function () {
    console.log("Alarm verwijderen");
    deleteAlarm(alarmID);
  });
}

const luisterNaarClickAdd = function() {
    document.querySelector(".js-add-alarm").addEventListener("click", function () {
      console.log("alarm opslaan");
      let lijst = document.querySelectorAll(".js-dag-btn");
      let herhaling = "";
      for(const element of lijst) {
        let aanuit = element.getAttribute("data-aanuit");
        herhaling += aanuit;
      }      

      const body = JSON.stringify({
        titel: document.querySelector("#js-titel").value,
        tijdstip: document.querySelector("#js-uur").value,
        herhaling: herhaling,
        lichteffect: document.querySelector("#js-kleur-modus").value ,
        deuntje: bestandMuziek,
        wekkerID: "1",
        idAlarm: alarmID,
        status: "1",
        kleur: document.querySelector("#js-kleur-2").value,
        kleurLedstrip: document.querySelector("#js-kleur-modus").value 
      });
      console.log(body);
      if(update == 1) {
        updateAlarm(body);     
      }
      else {
        voegAlarmToe(body);
      }
      
    });
  }

const home = function() {
  window.location.href = "/";
}
//#endregion
//#region ***  Data Access - get___ ***
const getMuziekjes = function() {
  handleData(`http://169.254.10.1:5000/api/muziekjes`, callbackMuziekjes);
};
const voegAlarmToe = function(body) {
  const url = `http://169.254.10.1:5000/api/alarmen`;
  handleData(url,home, console.log , ["POST"], body);
}
const updateAlarm = function(body) {
  const url = `http://169.254.10.1:5000/api/alarmen/update`;
  handleData(url,home, console.log , ["PUT"], body);
}
const getAlarmID = function(wekkerID,alarmID) {
  handleData(`http://169.254.10.1:5000/api/alarmen/${wekkerID}/${alarmID}`, callbackBewerken);
};
const deleteAlarm = function(alarmID) {
  handleData(`http://169.254.10.1:5000/api/alarmen/delete/${alarmID}`,home, console.log,["GET"]);
}
//#endregion
document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  listenToUI();
});
