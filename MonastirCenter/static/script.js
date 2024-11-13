function showClientButtons() {
    const clientButtons = document.getElementById('clientButtons');
    const reservationButtons = document.getElementById('reservationButtons');
  
    clientButtons.style.display = 'block';
    reservationButtons.style.display = 'none';
  }
  
  function showReservationButtons() {
    const clientButtons = document.getElementById('clientButtons');
    const reservationButtons = document.getElementById('reservationButtons');
  
    clientButtons.style.display = 'none';
    reservationButtons.style.display = 'block';
  }
  function showClientButtons() {
    document.getElementById("clientButtons").style.display = "block";
    document.getElementById("reservationButtons").style.display = "none";
    hideForms();
  }
  
  function showReservationButtons() {
    document.getElementById("clientButtons").style.display = "none";
    document.getElementById("reservationButtons").style.display = "block";
    hideForms();
  }
  
  function showClientForm() {
    document.getElementById("clientForm").style.display = "block";
    document.getElementById("reservationForm").style.display = "none";
  }
  
  function showReservationForm() {
    document.getElementById("clientForm").style.display = "none";
    document.getElementById("reservationForm").style.display = "block";
  }
  
  function hideForms() {
    document.getElementById("clientForm").style.display = "none";
    document.getElementById("reservationForm").style.display = "none";
  }
  