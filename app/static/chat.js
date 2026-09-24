(() => {
  const socket = io();
  const $ = (id) => document.getElementById(id);
  const messages = $("messages");
  let me = null;
  let typingTimer = null;

  function addItem(cls, content) {
    const li = document.createElement("li");
    li.className = cls;
    li.append(...content);
    messages.appendChild(li);
    messages.scrollTop = messages.scrollHeight;
  }

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    e.className = cls;
    e.textContent = text; // textContent avoids XSS from user input
    return e;
  }

  function renderMessage(m) {
    const time = new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    addItem(m.username === me ? "msg mine" : "msg", [
      el("span", "author", m.username),
      el("span", "time", time),
      el("div", "body", m.body),
    ]);
  }

  $("join-form").addEventListener("submit", (e) => {
    e.preventDefault();
    me = $("username").value.trim();
    const room = $("room").value.trim() || "general";
    if (!me) return;
    socket.emit("join", { username: me, room });
    $("room-label").textContent = "#" + room.toLowerCase();
    $("chat").classList.remove("hidden");
    $("message").focus();
  });

  $("message-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const body = $("message").value.trim();
    if (!body) return;
    socket.emit("message", { body });
    $("message").value = "";
  });

  $("message").addEventListener("input", () => socket.emit("typing"));

  socket.on("history", (list) => {
    messages.innerHTML = "";
    list.forEach(renderMessage);
  });
  socket.on("message", renderMessage);
  socket.on("system", (d) => addItem("system", [document.createTextNode(d.body)]));
  socket.on("error", (d) => addItem("system error", [document.createTextNode(d.body)]));
  socket.on("typing", (d) => {
    $("typing").textContent = `${d.username} is typing…`;
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => ($("typing").textContent = ""), 1500);
  });
  socket.on("disconnect", () => addItem("system error", [document.createTextNode("Disconnected — reconnecting…")]));
  socket.on("connect", () => {
    // Rejoin automatically after a reconnect (e.g. pod restart)
    if (me) socket.emit("join", { username: me, room: $("room-label").textContent.slice(1) });
  });
})();
