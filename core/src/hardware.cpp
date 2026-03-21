#include <iostream>
#include <fstream>
#include <string>
#include <unistd.h>

extern "C" {
    // Función para obtener la RAM total en MB
    long get_total_ram() {
        std::string token;
        std::ifstream file("/proc/meminfo");
        while (file >> token) {
            if (token == "MemTotal:") {
                unsigned long mem;
                if (file >> mem) {
                    return mem / 1024; // Convertir KB a MB
                }
            }
        }
        return -1;
    }

    // Función para obtener el número de núcleos del CPU
    int get_cpu_cores() {
        return sysconf(_SC_NPROCESSORS_ONLN);
    }
}

