from fastapi import WebSocket


# =========================================================
# WebSocket Connection Manager
# =========================================================
class ConnectionManager:

    def __init__(self):

        # =====================================================
        # Active Connections
        # =====================================================
        self.active_connections = []

        # =====================================================
        # Active Sessions
        # =====================================================
        self.sessions = {}


    # =====================================================
    # Connect Client
    # =====================================================
    async def connect(

        self,

        websocket: WebSocket,

        session_id: str = "default"
    ):

        await websocket.accept()

        self.active_connections.append(
            websocket
        )

        self.sessions[websocket] = session_id

        print(
            f"WebSocket Connected | "
            f"Session: {session_id} | "
            f"Total: {len(self.active_connections)}"
        )


    # =====================================================
    # Disconnect Client
    # =====================================================
    def disconnect(self, websocket: WebSocket):

        try:

            if websocket in self.active_connections:

                self.active_connections.remove(
                    websocket
                )

            if websocket in self.sessions:

                del self.sessions[websocket]

            print(
                f"WebSocket Disconnected | "
                f"Total: {len(self.active_connections)}"
            )

        except Exception as e:

            print(
                f"Disconnect Error: {e}"
            )


    # =====================================================
    # Send Personal Message
    # =====================================================
    async def send_personal_message(

        self,

        message: dict,

        websocket: WebSocket
    ):

        try:

            await websocket.send_json(
                message
            )

        except Exception as e:

            print(
                f"Send Message Error: {e}"
            )

            self.disconnect(
                websocket
            )


    # =====================================================
    # Broadcast Message
    # =====================================================
    async def broadcast(
        self,
        message: dict
    ):

        disconnected_clients = []

        for connection in self.active_connections:

            try:

                await connection.send_json(
                    message
                )

            except Exception:

                disconnected_clients.append(
                    connection
                )

        # =================================================
        # Cleanup Dead Connections
        # =================================================
        for connection in disconnected_clients:

            self.disconnect(
                connection
            )


    # =====================================================
    # Get Active Sessions
    # =====================================================
    def get_active_sessions(self):

        return len(self.active_connections)


# =========================================================
# Global WebSocket Manager
# =========================================================
manager = ConnectionManager()