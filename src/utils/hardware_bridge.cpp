#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unistd.h>

class HardwareBridge {
public:
    // RAM: Basado en /proc/meminfo (Universal)
    int get_mem_available() {
        std::ifstream file("/proc/meminfo");
        std::string line;
        long total = 0, avail = 0;
        while (std::getline(file, line)) {
            if (line.find("MemTotal:") == 0) total = extract_kb(line);
            if (line.find("MemAvailable:") == 0) avail = extract_kb(line);
        }
        if (total == 0) return -1;
        return (int)((avail * 100) / total); // Retorna % de RAM libre
    }

    // CPU: Calcula la carga basada en los ticks del sistema (Agnóstico)
    int get_cpu_load() {
        std::ifstream file("/proc/stat");
        std::string cpu;
        long user, nice, system, idle;
        file >> cpu >> user >> nice >> system >> idle;
        
        static long prev_idle = 0, prev_total = 0;
        long total = user + nice + system + idle;
        long diff_idle = idle - prev_idle;
        long diff_total = total - prev_total;
        
        prev_idle = idle;
        prev_total = total;

        if (diff_total == 0) return 0;
        return (int)(100 * (diff_total - diff_idle) / diff_total);
    }

private:
    long extract_kb(std::string line) {
        std::string num = "";
        for (char c : line) if (isdigit(c)) num += c;
        return (num.empty()) ? 0 : std::stol(num);
    }
};

extern "C" {
    HardwareBridge* Bridge_new() { return new HardwareBridge(); }
    int Bridge_get_ram_pct(HardwareBridge* b) { return b->get_mem_available(); }
    int Bridge_get_cpu_load(HardwareBridge* b) { return b->get_cpu_load(); }
}

