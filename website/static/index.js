function deleteNote(clickId) {
  fetch("/delete-click", {
    method: "POST",
    body: JSON.stringify({ clickId: clickId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

