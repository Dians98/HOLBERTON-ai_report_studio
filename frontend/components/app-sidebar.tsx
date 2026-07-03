import {
    Home,
    History,
    BarChart3,
    Settings,
    User
} from "lucide-react"

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarGroupContent,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar"

// LIENS DE NAVIGATIONS
const navigationItems = [
    { title: "Accueil", url: "/", icon: Home },
    { title: "Historique", url: "/history", icon: History },
    { title: "Rapports", url: "/report", icon: BarChart3 },
]

export function AppSidebar() {
    return (
        <Sidebar collapsible="icon">
            {/* --- En-tête : Logo ou Titre de l'application --- */}
            <SidebarHeader className="border-b px-4 py-2 flex items-center justify-between">
                <div className="flex items-center gap-2 font-bold text-lg">
                    <span className="h-6 w-6 rounded bg-primary text-primary-foreground flex items-center justify-center">
                        AI
                    </span>
                    <span className="group-data-[collapsible=icon]:hidden">Report Studio</span>
                </div>
            </SidebarHeader>

            {/* --- Contenu : Menu de Navigation principale --- */}
            <SidebarContent>
                <SidebarGroup>
                    <SidebarGroupLabel>Navigation</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {navigationItems.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton tooltip={item.title}>
                                        <a href={item.url} className="flex items-center gap-3">
                                            <item.icon className="h-4 w-4" />
                                            <span>{item.title}</span>
                                        </a>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>


            <SidebarFooter className="border-t p-4">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton >
                            <a href="/profile" className="flex items-center gap-3">
                                <span className="group-data-[collapsible=icon]:hidden font-medium">&copy; {new Date().getFullYear()} AI Report Studio. </span>
                            </a>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    )
}