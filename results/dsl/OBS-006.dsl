workspace "Lecteur d'articles" {

    model {
        lecteur = person "Lecteur"
        applicationLecture = softwareSystem "Application de lecture"

        lecteur -> applicationLecture "Lit des articles"
    }

    views {
        systemContext applicationLecture "SystemContext" {
            include *
            autoLayout
        }
    }
}
