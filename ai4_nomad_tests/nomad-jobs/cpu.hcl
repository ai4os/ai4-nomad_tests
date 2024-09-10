job "nomad-tests-cpu" {
  type      = "service"
  id        = "nomad-tests-cpu"
  priority  = "50"

  constraint {
    attribute = "${node.unique.id}"
    operator  = "="
    value     = "${NODE_ID}"
  }

  group "usergroup" {

    network {
      port "api" {
        to = 5000
      }
    }

    # We append a random UUID to the route and URL because it can happen that sometimes
    # containers remain dangling: unseen by Nomad, but parsedby Consul, and therefore
    # parsed by Traefik. So Traefik sees two routers/URLs with same name and crashes.

    # You have to SSH that node and manually delete the container.
    # But as these tests a running periodically we prefer remain on the safe side and
    # avoid this error altogether.

    # For the UUID we use only the 8 first characters `str(uuid.uuid1())[:8]` to avoid
    # going over the max domain length.

    service {
      name = "nomad-tests-cpu-api0-${UUID}"
      port = "api"
      tags = [
        "traefik.enable=true",
        "traefik.http.routers.nomad-tests-cpu-api0-${UUID}.tls=true",
        "traefik.http.routers.nomad-tests-cpu-api0-${UUID}.rule=Host(`api0-nomad-tests-cpu-${UUID}.${DOMAIN_0}`, `www.api0-nomad-tests-cpu-${UUID}.${DOMAIN_0}`)",
      ]
    }

    service {
      name = "nomad-tests-cpu-api1-${UUID}"
      port = "api"
      tags = [
        "traefik.enable=true",
        "traefik.http.routers.nomad-tests-cpu-api1-${UUID}.tls=true",
        "traefik.http.routers.nomad-tests-cpu-api1-${UUID}.rule=Host(`api1-nomad-tests-cpu-${UUID}.${DOMAIN_1}`, `www.api1-nomad-tests-cpu-${UUID}.${DOMAIN_1}`)",
      ]
    }

    service {
      name = "nomad-tests-cpu-api2-${UUID}"
      port = "api"
      tags = [
        "traefik.enable=true",
        "traefik.http.routers.nomad-tests-cpu-api2-${UUID}.tls=true",
        "traefik.http.routers.nomad-tests-cpu-api2-${UUID}.rule=Host(`api2-nomad-tests-cpu-${UUID}.${DOMAIN_2}`, `www.api2-nomad-tests-cpu-${UUID}.${DOMAIN_2}`)",
      ]
    }

    ephemeral_disk {
      size = 500
    }

    task "main" {

      driver = "docker"

      config {
        image   = "ai4oshub/ai4os-demo-app:latest"
        command = "deep-start"
        args    = ["--deepaas"]
        ports   = ["api"]
        storage_opt = {
          size = "500M"
        }
      }

      resources {
        cores  = 1
        memory = 500
      }
    }
  }
}