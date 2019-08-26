// Copyright 2019 VMware, Inc.
// SPDX-License-Indentifier: Apache-2.0

#include "template-engine.h"
#include "default-json-loader.h"
#include "stats.h"
#include <chrono>
#include <getopt.h>

int main(int argc, char **argv) {
  static std::string short_options = "b:e:vsdrt:h";
  static struct option long_options[] = {
      {"binding-data-resources", required_argument, 0, 0},
      {"env", 0, 0, 0},
      {"verbose", no_argument, 0, 0},
      {"stats", 0, 0, 0},
      {"debug", 0, 0, 0},
      {"raw", 0, 0, 0},
      {"help", 0, 0, 0},
      {0, 0, 0, 0}};
  std::vector<std::string> binding_file_list;
  std::string env_string;
  bool verbose = false;
  bool stats = false;
  bool debug = false;
  bool raw = false;
  int c;
  while (true) {
    int option_index = 0;
    c = getopt_long(argc, argv, short_options.c_str(), long_options,
                    &option_index);
    if (c == -1) {
      break;
    }
    switch (c) {
    case 0:
      if (long_options[option_index].flag != 0) {
        break;
      }
      std::cout << "option " << long_options[option_index].name;
      if (optarg) {
        std::cout << " with arg " << optarg;
      }
      std::cout << std::endl;
      break;
    case 'b':
      binding_file_list = jsonteng::Utils::split_string(optarg, ';');
      break;
    case 'e':
      env_string = optarg;
      break;
    case 'v':
      verbose = true;
      break;
    case 's':
      stats = true;
      break;
    case 'd':
      debug = true;
      break;
    case 'r':
      raw = true;
      break;
    case 'h':
      std::cout
          << "jsonteng [-h|--help] -b|--binding-data-list <list1;list2;...> "
             "[-e|--env <JSON>] [-v|--verbose] [-s|--stats] [-d|--debug] "
             "[-r|raw] <main-template>"
          << std::endl;
      exit(0);
    default:
      std::cout << "getopt_long returned unhandled charactor code " << c
                << std::endl;
    }
  }
  std::vector<nlohmann::json> binding_data_list;
  jsonteng::DefaultJsonLoader loader("", verbose);
  for (auto file_name : binding_file_list) {
    try {
      nlohmann::json binding_data = loader.load(file_name);
      binding_data_list.push_back(binding_data);
      loader.unload(file_name);
    } catch (jsonteng::TemplateEngineException &e) {
      std::cout << e.what() << std::endl;
      exit(-1);
    }
  }
  nlohmann::json env_binding = nlohmann::json::object();
  if (!env_string.empty()) {
    try {
      env_binding = loader.load(env_string);
      loader.unload(env_string);
    } catch (jsonteng::TemplateEngineException &e) {
      std::cout << e.what() << std::endl;
      exit(-1);
    }
  }
  if ((argc - optind) != 1) {
    std::cout << "Require one arg only" << std::endl;
    exit(-1);
  }
  std::string main_template = argv[optind];

  if (debug) {
    std::cout << "env data: " << env_binding.dump() << std::endl;
    std::cout << "binding data: " << std::endl;
    for (auto binding_data : binding_data_list) {
      std::cout << binding_data.dump() << std::endl;
    }
    std::cout << "main template: " << main_template << std::endl;
  }
  try {
    jsonteng::TemplateEngine engine(env_binding, nullptr, verbose);
    auto start_time = std::chrono::high_resolution_clock::now();
    nlohmann::json resolved_json =
        engine.resolve(main_template, binding_data_list);
    auto end_time = std::chrono::high_resolution_clock::now();
    if (verbose) {
      for (auto dup_param : engine.get_duplicated_parameters()) {
        std::cout << "Warning: Parameter " << dup_param.first
                  << " has duplicated values" << std::endl;
      }
      auto delta =
          std::chrono::duration<float, std::milli>(end_time - start_time)
              .count();
      std::cout << "Resolved JSON in " << delta << " ms" << std::endl;
    }
    if (raw) {
      std::cout << resolved_json.dump() << std::endl;
    } else {
      std::cout << resolved_json.dump(2, ' ', true) << std::endl;
    }
    if (stats) {
      std::cout << "Parameter usage" << std::endl;
      std::cout << "{";
      auto stats = engine.get_stats();
      auto it = stats.begin();
      auto end = stats.end();
      if (it != end) {
        std::cout << std::endl << "  \"" << it->first << "\": " << it->second;
        it++;
      }
      for (; it != end; it++) {
        std::cout << "," << std::endl
                  << "  \"" << it->first << "\": " << it->second;
      }
      std::cout << std::endl << "}" << std::endl;
    }
  } catch (jsonteng::TemplateEngineException &e) {
    std::cout << e.what() << std::endl;
    exit(-1);
  }
}