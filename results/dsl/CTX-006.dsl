workspace "Application Client" {

    model {
        client = person "Client"
        application = softwareSystem "Application"

        client -> application "Utilise"
    }

    views {
        systemContext application "SystemContext" {
            include *
            autoLayout
        }
    }
}
