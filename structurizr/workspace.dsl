workspace {
    model {
        // Personnes
        dev = person "Développeur" "Intègre les API de paiement et les SDK."
        merchant = person "Commerçant" "Gère son activité e-commerce et suit ses ventes."
        fintech = person "Fintech" "Partenaire utilisant la passerelle sous supervision."
        bank = person "Banque" "Institution financière membre distribuant la solution."
        client = person "Client final" "Effectue les achats en ligne."

        // Système Etudié
        gatewaySystem = softwareSystem "Gateway e-commerce GIM-UEMOA" "Passerelle de paiement unifiée en marque blanche."

        // Systèmes Externes
        gimSwitch = softwareSystem "Gim-switch" "Switch monétique régional pour les cartes."
        piSpi = softwareSystem "PI-SPI" "Interface de paiement et services interbancaires."
        gestionFraude = softwareSystem "Gestion fraude" "Module d'évaluation et de scoring des risques."
        threeDSecure = softwareSystem "3DS secure" "Serveur d'authentification forte."

        // Interactions (Niveau 1 uniquement)
        dev -> gatewaySystem "Intègre l'API"
        merchant -> gatewaySystem "Utilise les services de paiement"
        fintech -> gatewaySystem "Accède aux services"
        bank -> gatewaySystem "Paramètre et administre"
        client -> gatewaySystem "Paie en ligne"

        gatewaySystem -> gimSwitch "Route les transactions cartes"
        gatewaySystem -> piSpi "Interagit avec les services PI-SPI"
        gatewaySystem -> gestionFraude "Vérifie la fraude"
        gatewaySystem -> threeDSecure "Exécute l'authentification 3DS"
    }

    views {
        systemContext gatewaySystem "ContextDiagram" {
            include *
            autoLayout lr
        }
    }
}