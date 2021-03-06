#include <signal.h>
#include <boost/program_options.hpp>
#include <boost/format.hpp>
#include <iostream>
#include <fstream>
#include <sstream>
#include <map>
#include <vector>
#include <list>
#include <algorithm>

//#define DEBUG_ON
#define RANDOM_SEED

#ifdef DEBUG_ON
#define DEBUG(x) do { std::cerr << x; } while (0)
#else
#define DEBUG(x)
#endif


// TODO: don't use namespace std.  In retrospect I think this is bad practice.
using namespace std;
using boost::format;
namespace po = boost::program_options;

bool quit = false;

void sigint_handler(int s) {
    cerr << endl;
    quit = true;
}

enum msg {NONE=0x4, ERASE=0x2, ONE=0x1, ZERO=0x0};

class Variable;
class Check;

typedef list<Variable *> list_var;
typedef list<Variable *>::iterator list_var_it;
typedef vector<Variable *> vec_var;
typedef vector<Variable *>::iterator vec_var_it;
typedef map<Variable*, msg> map_var_msg;
typedef map<Variable*, msg>::iterator map_var_val_it;

typedef list<Check *> list_chk;
typedef list<Check *>::iterator list_chk_it;
typedef vector<Check *> vec_chk;
typedef vector<Check *>::iterator vec_chk_it;
typedef map<Check*, msg> map_chk_val;
typedef map<Check*, msg>::iterator map_chk_val_it;

class Check {
public:
    unsigned int index;
    Check(int _index);
    vec_var vars;
    int add_variable(Variable *v);
    bool send_messages();
};

class Variable {
public:
    unsigned int index;
    msg value;
    Variable(int _index);
    int apply_channel(double p_e);
    map_chk_val chks;
    vector<msg> mailbox;
    msg update_value();

};


Check::Check(int _index) {
    index = _index;
    DEBUG("check " << index << " @" << this << " created" << endl);
}
bool Check::send_messages() {
    bool sent_erasure = false;
    // loop through each connected variable node
    for(Variable *v_target : this->vars) {
        if(v_target->value != ERASE) {
            continue;
        }
        DEBUG("c" << this->index << " sending to v" << v_target->index << " from ");
        // loop through all *other* connected variable nodes
        bool erased = false;
        for(Variable *v : this->vars) {
            if(v_target == v) {
                continue;
            }
            DEBUG("v" << v->index << " ");
            if(v->value == ERASE) {
                sent_erasure = true;
                erased = true;
                break;
            } 
            
        }
        DEBUG(endl);
        if(!erased) {
            v_target->mailbox.push_back(ZERO);
        }
    }
    return sent_erasure;
        
}



Variable::Variable(int _index) {
    this->index = _index;
    DEBUG("v" << this->index << " @" << this << " created" << endl);
    this->value = ZERO;
}

int Variable::apply_channel(double p_e) {
    double r = static_cast <double> (rand()) / static_cast <double> (RAND_MAX); 
    if(p_e > r) {
        this->value = ERASE;
    }
    return 0;
}

msg Variable::update_value() {
    // determine current value of variable
    if(this->value == ERASE) {
        // read in all messages and apply variable node rules
        for(msg c_msg : this->mailbox) {
        //for(map_chk_val_it it = this->chks.begin(); it != this->chks.end(); ++it) {
        //    msg c_msg = it->second;
            if(c_msg == ONE || c_msg == ZERO) {
                // if any messages is non erased, take value and stop looking
                this->value = c_msg;
                break;
            }
        }
    } else if (this->value != ONE && this->value != ZERO) {
        DEBUG("warning v" << this->index << " is undefined" << endl);
    }

    this->mailbox.clear();

    // send variable value out to connected check nodes
    msg u = this->value;
    return u;
   
}

class Graph {
public:
    vec_var vars;
    vec_chk chks;

    Check* get_check(unsigned int index) {
        Check *c;
        unsigned int size = chks.size();
        if(index >= size) {
            chks.resize(index+1);
            for(unsigned int i = size; i <= index; i++) {
                chks[i] = new Check(i);
            }
        }
        c = chks[index];
        return c;
    }

    Variable* get_variable(unsigned int index) {
        Variable *v;
        unsigned int size = vars.size();
        if(index >= size) {
            vars.resize(index+1);
            for(unsigned int i = size; i <= index; i++) {
                vars[i] = new Variable(i);
            }
        }
        v = vars[index];
        return v;
    }

    void print_checks() {
        for(unsigned int i = 0; i < chks.size(); i++) {
            Check* c = chks[i];
            cout << "check " << i << ":";
            for(vec_var_it it = c->vars.begin(); it != c->vars.end(); ++it) {
                cout << " " << (*it)->index;
            }
            cout << endl;
        }
    }

    void print_variables() {
        for(unsigned int i = 0; i < vars.size(); i++) {
            Variable* v = vars[i];
            cout << "v" << i << "=" << v->value << " : ";
            for(map_chk_val_it it = v->chks.begin(); it != v->chks.end(); ++it) {
                cout << " " << it->first->index;
            }
            cout << endl;
        }
    }

    int connect(int c_idx, int v_idx) {
        DEBUG("connecting: " << c_idx << "," << v_idx << endl);
        Check *c = this->get_check(c_idx);
        Variable *v = this->get_variable(v_idx);
        c->vars.push_back(v);
        v->chks[c] = NONE;
        return 0;
    }

    void zero_variables() {
        for(Variable *v : this->vars) {
            v->value = ZERO;
        }
    }

    int apply_channel(double p_e) {
        for(Variable *v : this->vars) {
            v->apply_channel(p_e);
            DEBUG("v" << v->index << " value: " << v->value << endl);
        }
        return 0;
    }

    void print_var_vec() {
        for(Variable *v : this->vars) {
            cout << v->value;
        }
        cout << endl;
    }

    int decode(int termination_size, int window_size, int constraint_length, double p_e, int iterations) {
        // TODO: stop when no erasures remain

        unsigned int constraint_window = this->chks.size() / (termination_size+1);
        //cout << this->chks.size() << " " << termination_size << " " << constraint_window << endl;

        // run check step

        DEBUG("decoding..." << endl);

        unsigned int bit_errors = 0;

        //cout << constraint_length << endl;
        if(termination_size == 0) {
            termination_size = 1;
        }

        list_var active_variables;
        list_chk active_checks;
        for(int i = 0; i < termination_size-window_size+1; ++i) {
            list_chk next_checks;
            list_var next_variables;

            active_variables.clear();
            active_checks.clear();

            int win_start_var = i * constraint_length;
            int win_end_var = win_start_var + window_size*constraint_length;
            for(int j = win_start_var; j < win_end_var; ++j) {
                Variable *v = vars[j];
                if(v->value == ERASE) {
                    active_variables.push_back(v);
                    for(map_chk_val::iterator it = v->chks.begin(); it != v->chks.end(); ++it) {
                        active_checks.push_back(it->first);  // this will add duplicates
                    }
                }
            }

            unsigned int last_chk_size=0,cur_chk_size=-1;
            unsigned int last_var_size=0,cur_var_size=-1;
            for(int j = 0; j < iterations; ++j) {
                last_chk_size = cur_chk_size;
                last_var_size = cur_var_size;
                cur_chk_size = active_checks.size();
                cur_var_size = active_variables.size();

                if( (cur_chk_size == 0 && cur_var_size == 0) || (cur_chk_size == last_chk_size && cur_var_size == last_var_size) ) {
                    break;
                }
                next_checks.clear();
                next_variables.clear();

                for(Check *c : active_checks) {
                    bool sent_erasure = c->send_messages();
                    if(sent_erasure) {
                        next_checks.push_back(c);
                    }
                }
                active_checks = next_checks;

                for(Variable *v : active_variables) {
                    
                    if(v->update_value() == ERASE) {
                        next_variables.push_back(v);
                    }
                }
                active_variables = next_variables;

            }
           
        }
        // Only check errors after pipeline is full
        // Check errors on last constraint length bits only - these are about to be shifted out.
        if(active_variables.size() > 0) {
            for(Variable *v : this->vars) {
                if(v->value != ZERO) {
                    ++bit_errors;
                }
            }
        }
        return bit_errors;
    }

    double test_ber(unsigned int termination_size, unsigned int window_size, unsigned int constraint_length, double p_e, unsigned int iterations, unsigned int block_error_threshold) {
        unsigned int block_error_count = 0;
        unsigned int bit_error_count = 0;
        unsigned int sim_count = 0;
        unsigned long long max_bit_count = 1E8;
        unsigned long long update_interval = block_error_threshold / 20;
        unsigned long long bit_count ;

        //cerr << update_interval;
        while(block_error_count <= block_error_threshold) {
            this->zero_variables();
            this->apply_channel(p_e);
            unsigned int bit_errors = this->decode(termination_size, window_size, constraint_length, p_e, iterations);
            if(quit) {
                return -1;
            }
            if(bit_errors) {
                block_error_count++;
                bit_error_count += bit_errors;

                if(block_error_count % update_interval == 0) {
                    double percent = 100. * ((double)block_error_count / (double)block_error_threshold) ;
                    cerr << percent << "%," ;
                }
            }

            sim_count++;

            bit_count = this->vars.size()*sim_count;
            if(bit_count > max_bit_count){
                break;  // if we can't get any errors we should abort
            }
        }

        double ber = (double)bit_error_count/(double)(bit_count);
        return ber;
    }
};




int main(int argc, char** argv) {
    #ifdef RANDOM_SEED
    srand ( time(NULL) );
    #endif

    string parity_check_file;
    unsigned int window_size;
    unsigned int decode_iters;
    unsigned int term_size;
    unsigned int block_errors;
    double pe_start, pe_stop;
    unsigned int pe_num;

    try {
        //setup the program options
        po::options_description desc("Allowed options");
        desc.add_options()
            ("help,h", "help message")
            ("parity-file", po::value<std::string>(&parity_check_file)->required(), "parity check matrix file")
            ("wsize", po::value<unsigned int>(&window_size)->default_value(1), "window size of decoder")
            ("iter", po::value<unsigned int>(&decode_iters)->default_value(100), "number decoding iterations")
            ("term", po::value<unsigned int>(&term_size)->default_value(100), "termination length of data")
            ("blocks", po::value<unsigned int>(&block_errors)->default_value(100), "number block errors")
            ("start", po::value<double>(&pe_start)->default_value(0.4), "start erasure probability")
            ("stop", po::value<double>(&pe_stop)->default_value(1.0), "stop erasure probability")
            ("num", po::value<unsigned int>(&pe_num)->default_value(10), "number of erasure probabilities to test")
        ;
        po::variables_map vm;
        po::positional_options_description p;
        p.add("parity-file", -1);
        po::store(po::command_line_parser(argc, argv).options(desc).positional(p).run(), vm);

        if (vm.count("help")) {
            cout << desc << "\n";
            return false;
        }

        po::notify(vm);

    } catch(exception &e) {
        cerr << "error: " << e.what() << endl;
        return -1;
    }

    Graph g;
    string line;
    int v_idx=0, c_idx=0, max_v_idx = 0;
    typedef vector<unsigned int> vec_int;
    vector<vec_int*> checks;
    ifstream myfile (parity_check_file.c_str());
    if( myfile.is_open() ) {
        while (getline(myfile, line)) {
            istringstream iss(line);
            vec_int *check = new vec_int;
            checks.push_back(check);
            while (iss >> v_idx) {
                if(v_idx > max_v_idx) {
                    max_v_idx = v_idx;
                }
                check->push_back(v_idx-1);
            } 
            c_idx++;
        }
    } else {
        cerr << "error: unable to open " << parity_check_file << endl;
        return -1;
    }

    if(term_size == 0) {
        for(vector<vec_int*>::iterator c_it = checks.begin(); c_it != checks.end(); ++c_it) {
            vec_int *check = *c_it;
            int c_idx = (c_it) - checks.begin();
            for(vec_int::iterator v_it = check->begin(); v_it != check->end(); ++v_it) {
                v_idx = *v_it;
                g.connect(c_idx, v_idx);
            }
        }
    } else {
        unsigned int var_check_ratio = max_v_idx / checks.size();
        int c_idx = 0;
        for(unsigned int i = 0; i < term_size; ++i) {
            for(vector<vec_int*>::iterator c_it = checks.begin(); c_it != checks.end(); ++c_it) {
                int c_idx = c_it - checks.begin();
                vec_int *check = *c_it;
                for(vec_int::iterator v_it = check->begin(); v_it != check->end(); ++v_it) {
                    v_idx = *v_it;
                    if(v_idx <= c_idx*(var_check_ratio+1) ) {
                        g.connect(c_idx+i*checks.size(), v_idx+i*max_v_idx);
                    } else {
                        g.connect(c_idx+(i+1)*checks.size(), v_idx+i*max_v_idx);
                    }
                }
            }
        }
    }
    //g.print_checks();
    //return 0;

    signal (SIGINT,sigint_handler);

    double pe_step = (pe_stop - pe_start) / (pe_num-1);
    vector<double> pe_values;
    vector<double> ber_values;

    pe_values.push_back(pe_start);
    for(unsigned i = 1; i < pe_num; ++i) {
       pe_values.push_back(pe_start + i*pe_step);
    }

    // TODO put these on arguments
    unsigned int const_len = max_v_idx;


    for(vector<double>::iterator it = pe_values.begin(); it != pe_values.end(); ++it) {
        double pe = *it;
        unsigned int index = it - pe_values.begin() + 1;
        cerr << format("[%2d/%2d] p=%1.4f...") % index % pe_values.size() % pe;
        double ber = g.test_ber(term_size, window_size, const_len, pe, decode_iters, block_errors);
        if(quit) {
            break;
        }
        ber_values.push_back(ber);
        cerr << format("%.3e") % ber << endl;
    }

    for( double pe : pe_values ) {
        cout << pe << " " ;
    }
    cout << endl;
    for( double ber : ber_values ) {
        cout << ber << " " ;
    }
    cout << endl;

    return 0;
}


