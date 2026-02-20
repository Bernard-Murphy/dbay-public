import { ref, onMounted, onUnmounted } from "vue";

export function useWebSocket(url: string) {
  const socket = ref<WebSocket | null>(null);
  const isConnected = ref(false);
  const messages = ref<any[]>([]);

  function connect() {
    socket.value = new WebSocket(url);

    socket.value.onopen = () => {
      isConnected.value = true;
      console.log("WebSocket connected");
    };

    socket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        messages.value.push(data);
      } catch (e) {
        console.error("WebSocket message error", e);
      }
    };

    socket.value.onclose = () => {
      isConnected.value = false;
      console.log("WebSocket disconnected");
      // Reconnect logic?
      setTimeout(connect, 5000);
    };

    socket.value.onerror = (error) => {
      console.error("WebSocket error", error);
    };
  }

  function send(data: any) {
    if (socket.value && isConnected.value) {
      socket.value.send(JSON.stringify(data));
    }
  }

  function subscribe(listingId: string) {
    send({ action: "subscribe", listing_id: listingId });
  }

  function unsubscribe(listingId: string) {
    send({ action: "unsubscribe", listing_id: listingId });
  }

  onMounted(() => {
    connect();
  });

  onUnmounted(() => {
    if (socket.value) {
      socket.value.close();
    }
  });

  return {
    socket,
    isConnected,
    messages,
    subscribe,
    unsubscribe,
  };
}
