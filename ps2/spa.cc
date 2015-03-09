#include <boost/algorithm/string.hpp>
#include <iostream>
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
    int apply_channel(float p_e);
    map_chk_val chks;
    msg update_value();

};


Check::Check(int _index) {
    index = _index;
    DEBUG("check " << index << " @" << this << " created" << endl);
}
bool Check::send_messages() {
    bool sent_erasure = false;
    // loop through each connected variable node
    for(vec_var_it i_it = this->vars.begin(); i_it != this->vars.end(); ++i_it) {
        Variable *v_target = *i_it;
        DEBUG("c" << this->index << " sending to v" << v_target->index << " from ");
        // loop through all *other* connected variable nodes
        msg msg_target = NONE;
        int parity = 0;
        for(vec_var_it j_it = this->vars.begin(); j_it != this->vars.end(); ++j_it) {
            Variable *v = *j_it;
            if(v_target == v) {
                continue;
            }
            DEBUG("v" << v->index << " ");
            msg v_value = v->value;
            if(v_value == ERASE) {
                sent_erasure = true;
                msg_target = ERASE;
                break;
            } else if(v_value == NONE) {
                DEBUG("warning: v" << v->index << endl);
            }

            parity += v_value; 
            msg_target = (parity&1) ? ONE : ZERO;
        }
        DEBUG(endl);
        //DEBUG("c" << this->index << " sending " << msg_target << " to v" << v_target->index << endl);
        v_target->chks[this] = msg_target;
    }
    return sent_erasure;
        
}



Variable::Variable(int _index) {
    this->index = _index;
    DEBUG("v" << this->index << " @" << this << " created" << endl);
    this->value = ZERO;
}

int Variable::apply_channel(float p_e) {
    float r = static_cast <float> (rand()) / static_cast <float> (RAND_MAX); 
    if(p_e > r) {
        this->value = ERASE;
    }
    return 0;
}

msg Variable::update_value() {
    // determine current value of variable
    if(this->value == ERASE) {
        // read in all messages and apply variable node rules
        for(map_chk_val_it it = this->chks.begin(); it != this->chks.end(); ++it) {
            //Check *c = it->first;
            msg c_msg = it->second;
            if(c_msg == ONE || c_msg == ZERO) {
                // if any messages is non erased, take value and stop looking
                this->value = c_msg;
                break;
            }
        }
    } else if (this->value != ONE && this->value != ZERO) {
        DEBUG("warning v" << this->index << " is undefined" << endl);
    }

    // send variable value out to connected check nodes
    msg u = this->value;
    /*
    for(map_chk_val_it it = this->chks.begin(); it != this->chks.end(); ++it) {
        Check *c = it->first;
        c->vars[this] = u;
    }
    */

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
        for(vec_var_it it = this->vars.begin(); it != this->vars.end(); ++it) {
            (*it)->value = ZERO;
        }
    }

    int apply_channel(float p_e) {
        for(vec_var_it it = this->vars.begin(); it != this->vars.end(); ++it) {
            (*it)->apply_channel(p_e);
            DEBUG("v" << (*it)->index << " value: " << (*it)->value << endl);
        }
        return 0;
    }

    void print_var_vec() {
        for(vec_var_it it = this->vars.begin(); it != this->vars.end(); ++it) {
            Variable *v = *it;
            cout << v->value;
        }
        cout << endl;
    }

    int decode(int iterations) {
        // TODO: stop when no erasures remain

        // run check step

        DEBUG("decoding..." << endl);

        list_chk active_checks;

        for(vec_chk_it it = this->chks.begin(); it != this->chks.end(); ++it) {
            active_checks.push_back(*it);
        }

        list_var active_variables;

        for(vec_var_it it = this->vars.begin(); it != this->vars.end(); ++it) {
            active_variables.push_back(*it);
        }

        for(int i = 0; i < iterations; ++i) {
            if(active_variables.size() == 0 && active_checks.size() == 0) {
                break;
            }

            /*for(vec_chk_it it = this->chks.begin(); it != this->chks.end(); ++it) {
                Check *c = *it;
                c->send_messages();
            }*/
            list_chk next_checks;
            for(list_chk_it it = active_checks.begin(); it != active_checks.end(); ++it) {
                Check *c = *it;
                bool sent_erasure = c->send_messages();
                if(sent_erasure) {
                    next_checks.push_back(c);
                }
            }
            active_checks = next_checks;

            /*for(vec_var_it it = this->vars.begin(); it != this->vars.end(); ++it) {
                Variable *v = *it;
                v->update_value();
            }*/
            list_var next_variables;
            for(list_var_it it = active_variables.begin(); it != active_variables.end(); ++it) {
                Variable *v = *it;
                v->update_value();
                if(v->value == ERASE) {
                    next_variables.push_back(v);
                }
            }
            active_variables = next_variables;
            //this->print_variables();
        }
        
        unsigned int bit_errors = 0;
        for(vec_var_it it = this->vars.begin(); it != this->vars.end(); ++it) {
            if((*it)->value != ZERO) {
                ++bit_errors;
            }
        }
        return bit_errors;
    }

    float test_ber(float p_e, unsigned int iterations, unsigned int block_error_threshold) {
        unsigned int block_error_count = 0;
        unsigned int bit_error_count = 0;
        unsigned int sim_count = 0;
        while(block_error_count <= block_error_threshold) {
            this->zero_variables();
            this->apply_channel(p_e);
            unsigned int bit_errors = this->decode(iterations);
            if(bit_errors) {
                block_error_count++;
                bit_error_count += bit_errors;
            }
            sim_count++;
        }
        float ber = (float)bit_error_count/(float)(sim_count*this->vars.size());
        return ber;
    }
};




int main(int argc, char** argv) {
    #ifdef RANDOM_SEED
    srand ( time(NULL) );
    #endif

    Graph g;
    string line;
    int v_idx=0, c_idx=0;
    while (getline(cin, line))
    {
        istringstream iss(line);
        while (iss >> v_idx) {
            g.connect(c_idx, v_idx-1);
        } 
        c_idx++;
    }
    //g.print_checks();
    //g.print_variables();

    float start_p_erase = 0.25;
    //float start_p_erase = 0.35;
    float stop_p_erase = 0.50;
    float step_p_erase = (stop_p_erase - start_p_erase) / 40.;

    cout << "epsilon ";
    for(float p_erase = start_p_erase; p_erase < stop_p_erase; p_erase+=step_p_erase) {
            cout << " " << p_erase;
    }
    cout << endl;

    int iter_list[] = {1,3,5,10,15,20,25,30};
    for(unsigned int i = 0; i < sizeof(iter_list); i++) {
        unsigned int iters = iter_list[i];
        cout << iters;
        for(float p_erase = start_p_erase; p_erase < stop_p_erase; p_erase+=step_p_erase) {
            unsigned int block_errors = 100;
            cout << " " << g.test_ber(p_erase, iters, block_errors);
        }
        cout << endl;
    }

}


        //cout << "check " << c << " variables:" << endl;
        //copy(int_vars.begin(), int_vars.end(), ostream_iterator<int>(cout, " "));
