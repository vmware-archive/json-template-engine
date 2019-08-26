CXX := g++
SRCDIR := ./src/main/c++
BUILDDIR := ./build/c++
OBJDIR := $(BUILDDIR)/objs
DEPDIR	:= $(BUILDDIR)/deps

SRCS := $(wildcard $(SRCDIR)/cli/*.cpp)
CLI := $(BUILDDIR)/jsonteng
OBJFILES := $(foreach obj,$(SRCS:%.cpp=%.o),$(OBJDIR)/$(subst $(SRCDIR)/,,$(obj)))
DEPFILES := $(foreach dep,$(SRCS:%.cpp=%.d),$(DEPDIR)/$(subst $(SRCDIR)/,,$(dep)))


CXXFLAGS = -c -g3 -std=c++17 -fPIC -Wall -I$(SRCDIR)/include -I../tag_contributions/src/main/c++/include -I$(SRCDIR)/ext/json
DEPFLAGS = -MT $@ -MMD -MP -MF $(DEPDIR)/$*.d

COMPILE.c = $(CXX) $(DEPFLAGS) $(CXXFLAGS) $(TARGET_ARCH)

$(OBJDIR)/%.o: $(SRCDIR)/%.cpp $(DEPDIR)/%.d
	@mkdir -p $(dir $@) $(dir $(DEPDIR)/$*.d)
	$(COMPILE.c) $(OUTPUT_OPTION) $<

$(DEPFILES):

cli: $(CLI)

$(CLI): $(OBJFILES)
	$(CXX) -g3 -std=c++17 $^ -o $@_$(JSONTENG_BUILD_VERSION)
	tar czf $(BUILDDIR)/source_c++_$(JSONTENG_BUILD_VERSION).tgz -C $(SRCDIR) .

clean:
	@rm -rf $(BUILDDIR)

include $(wildcard $(DEPFILES))
