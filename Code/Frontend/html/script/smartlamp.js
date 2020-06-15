const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let html_smartlamp;
let html_statuslamp;
let html_kleur;
let huidigeModus = "";
let btnPower;

const listenToUI = function () {
  html_statuslamp = document.querySelector(".js-status-lamp");
  html_smartlamp = document.querySelector(".js-smart-light-bg");
  html_smartlamp.addEventListener("click", changeStatusLamp);
  //Kleuren toevegen aan de dropdown
  html_kleur = document.querySelector(".js-kleur");  
  html_kleur.addEventListener("change", changeKleurLamp);
  btnPower = document.getElementById('btnPower');
  btnPower.addEventListener("click",shutdown)
};

const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
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
    else if (jsonObject.status == 'gewoon'){
      html_smartlamp.style.backgroundColor = "#F16A38";
    }
    html_statuslamp.innerHTML = `<h2 class="">${jsonObject.status}</h2>`;

    let kleur = ["uit","gewoon", "flikker", "kleur"];
    let kleurnaam = ["Uit","Zonlicht simulatie","Flikkerend licht", "Kleurenwiel"]
    let htmlstring = ``;
    console.log(huidigeModus);

    if(jsonObject.status != huidigeModus) {
      for(let i = 0; i < 4;i++) {
        if(jsonObject.status == kleur[i]) {
          huidigeModus = kleur[i];
          htmlstring += `<option value="${kleur[i]}" selected>${kleurnaam[i]}</option>`;
        }
        else {
          htmlstring += `<option value="${kleur[i]}">${kleurnaam[i]}</option>`;
        }
        
      }
      html_kleur.innerHTML = htmlstring;
    }
    
    //To do onchange event koppelen
  });
};
//#region ***  Callbacks***

//#endregion

//#region ***  Clicks  ***
const shutdown = function() {
  socket.emit("F2B_shutdown");
}

const changeStatusLamp = function() {
  html_smartlamp.style.backgroundColor = "#ffffff";
  html_statuslamp.innerHTML = `<h2 class="">Uit</h2>`;  
  updateOnOffLamp(1);
};

const changeKleurLamp = function() {
  let e = document.getElementById("js-kleur-modus");
  let kleurmodus = e.options[e.selectedIndex].value;
  updateStatus(1,kleurmodus);
}
//#region ***  Data Access - get___ ***
const updateOnOffLamp = function(wekkerID) {
  handleData(`http://169.254.10.1:5000/api/smartlamp/changeOnOff/${wekkerID}`,console.log, console.log,["PUT"]);  
};
const updateStatus = function(wekkerID,status) {
  handleData(`http://169.254.10.1:5000/api/smartlamp/changeStatus/${wekkerID}/${status}`,console.log, console.log,["PUT"]);  
};
//#endregion
document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  listenToUI();
  listenToSocket();
});
