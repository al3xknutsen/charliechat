from core.file_manager import FILE_WRITE
from core.global_vars import appdata
from core.time_manager import now
from windows.window_addserver import AddServerWindow


class ServerManager:
    def add_server(self, event):
        '''Add server when pressing the "Add server" button.
        Displays a window for the user to input server settings.'''
        addserver = AddServerWindow(self, self.serverdata)  # Show window

        if addserver.proceed:
            addr = addserver.serveraddr
            port = addserver.serverport

            self.write_log(now(), "You added server: " + addr)

            self.serverdata[addr] = port  # Add server to list
            self.chatroomdata[addr] = {"public": {}, "private": {}}
            self.seconds[addr] = {}

            # Save and show in list
            FILE_WRITE(self.paths["rooms"], self.chatroomdata)
            FILE_WRITE(self.paths["servers"], self.serverdata)
            self.servers.Append(addr)

    def switch_server(self, event):
        '''Switching server when clicking a server in the server list.'''
        server = self.servers.GetStringSelection()
        addr = server if server else self.host

        FILE_WRITE(appdata + "new_server.txt", [addr, self.serverdata[addr]])
        self.quit(None)