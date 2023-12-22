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

    service {
      name = "nomad-tests-cpu-api0"
      port = "api"
      tags = [
        "traefik.enable=true",
        "traefik.http.routers.nomad-tests-cpu-api0.tls=true",
        "traefik.http.routers.nomad-tests-cpu-api0.rule=Host(`api-nomad-tests-cpu.${DOMAIN_0}`, `www.api-nomad-tests-cpu.${DOMAIN_0}`)",
      ]
    }

    service {
      name = "nomad-tests-cpu-api1"
      port = "api"
      tags = [
        "traefik.enable=true",
        "traefik.http.routers.nomad-tests-cpu-api1.tls=true",
        "traefik.http.routers.nomad-tests-cpu-api1.rule=Host(`api-nomad-tests-cpu.${DOMAIN_1}`, `www.api-nomad-tests-cpu.${DOMAIN_1}`)",
      ]
    }

    service {
      name = "nomad-tests-cpu-api2"
      port = "api"
      tags = [
        "traefik.enable=true",
        "traefik.http.routers.nomad-tests-cpu-api2.tls=true",
        "traefik.http.routers.nomad-tests-cpu-api2.rule=Host(`api-nomad-tests-cpu.${DOMAIN_2}`, `www.api-nomad-tests-cpu.${DOMAIN_2}`)",
      ]
    }

    ephemeral_disk {
      size = 500
    }

    task "usertask" {

      driver = "docker"

      config {
        image   = "deephdc/deep-oc-demo_app:latest"
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