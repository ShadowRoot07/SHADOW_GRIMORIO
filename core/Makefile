# Configuración para Termux (Clang)
CXX = clang++
CXXFLAGS = -fPIC -shared -O3
TARGET = ../../src/utils/libhardware.so

all: $(TARGET)

$(TARGET): src/hardware.cpp
	@mkdir -p ../../src/utils
	$(CXX) $(CXXFLAGS) src/hardware.cpp -o $(TARGET)
	@echo "✨ Núcleo C++ forjado en: $(TARGET)"

clean:
	rm -f $(TARGET)

