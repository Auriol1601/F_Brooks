workspace "Plateforme de crédit" {

    model {
        client = person "Client"
        plateformeCredit = softwareSystem "Plateforme de crédit"
        serviceScoring = softwareSystem "Service externe de scoring"

        client -> plateformeCredit "Utilise"
        plateformeCredit -> serviceScoring "Utilise pour évaluer les demandes"
    }

    views {
        systemContext plateformeCredit "SystemContext" {
            include *
            autoLayout
        }
    }
}
