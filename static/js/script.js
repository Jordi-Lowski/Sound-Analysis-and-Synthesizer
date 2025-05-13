let currentPlotFileName = "";
let currentPlotType = "";

function openModal(file_name, plot_type) {
  currentPlotFileName = file_name;
  currentPlotType = plot_type;
  let url = "";
  if (plot_type === "fft") {
    url = "/plot/" + file_name + "/fft";
  } else if (plot_type === "comparison") {
    url = "/plot/" + file_name + "/comparison";
  }
  document.getElementById("modal-img").src = url;
  document.getElementById("comparison-img").style.display = "none";
  document.querySelector('.plot-container').classList.add('single');
  document.getElementById("modal").classList.add("open");
}

function closeModal() {
  document.getElementById("modal").classList.remove("open");
  document.getElementById("comparison-img").style.display = "none"; 
  document.getElementById("comparison-dropdown").style.display = "none"; 
}

function downloadDiagram(fileName = 'FrequencyPlot') {
  const modalImg = document.getElementById('modal-img');
  const link = document.createElement('a');
  link.href = modalImg.src; 
  link.download = fileName;
  link.click();
}

function openComparisonDropdown() {
  const dropdown = document.getElementById("comparison-dropdown");
  dropdown.style.display = "block";
  populateNoteDropdown();
}

function populateNoteDropdown() {
  const noteSelect = document.getElementById("note-select");
  noteSelect.innerHTML = "";
  const currentGuitarType = document.body.getAttribute('data-guitar-type').toLowerCase();
  
  fetch(`/api/measurements?all_types=true`)
    .then(response => response.json())
    .then(data => {
      const acousticGroup = document.createElement("optgroup");
      acousticGroup.label = "Acoustic Guitar";
      
      const westernGroup = document.createElement("optgroup");
      westernGroup.label = "Western Guitar";
      
      data.forEach(measurement => {
        const option = document.createElement("option");
        option.value = measurement.file_name;
        option.textContent = `${measurement.note} (${measurement.file_name})`;
        
        if (measurement.type === 'acoustic') {
          acousticGroup.appendChild(option);
        } else if (measurement.type === 'western') {
          westernGroup.appendChild(option);
        }
      });
      
      if (acousticGroup.children.length > 0) {
        noteSelect.appendChild(acousticGroup);
      }
      
      if (westernGroup.children.length > 0) {
        noteSelect.appendChild(westernGroup);
      }
    })
    .catch(error => console.error("Error fetching measurements:", error));
}

function loadComparisonPlot() {
  const selectedFileName = document.getElementById("note-select").value;
  if (!selectedFileName) return;
  const url = `/plot/${selectedFileName}/${currentPlotType}`;
  document.getElementById("comparison-img").src = url;
  document.getElementById("comparison-img").style.display = "block";
  document.querySelector('.plot-container').classList.remove('single');
}

function populateSearchDropdown() {
  const searchDropdown = document.getElementById("search-dropdown");
  searchDropdown.innerHTML = "";
  const guitarType = document.body.getAttribute('data-guitar-type').toLowerCase();
  
  fetch(`/api/measurements?type=${guitarType}`)
    .then(response => response.json())
    .then(data => {
      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = "Select a note...";
      searchDropdown.appendChild(defaultOption);
      const AllNotesOption = document.createElement("option");
      AllNotesOption.value = "";
      AllNotesOption.textContent = "All Notes";
      searchDropdown.appendChild(AllNotesOption);
      data.forEach(measurement => {
        const option = document.createElement("option");
        option.value = measurement.file_name;
        option.textContent = `${measurement.note} (${measurement.file_name})`;
        searchDropdown.appendChild(option);
      });
    })
    .catch(error => console.error("Error fetching measurements for search:", error));
}

window.addEventListener('DOMContentLoaded', populateSearchDropdown);

