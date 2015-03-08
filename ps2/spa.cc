#include <boost/algorithm/string.hpp>
#include <iostream>
#include <sstream>
#include <map>
#include <vector>
#include <algorithm>

#define DEBUG_ON

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

typedef vector<Variable *> vec_var;
typedef vector<Variable *>::iterator vec_var_it;
typedef map<Variable*, msg> map_var_msg;
typedef map<Variable*, msg>::iterator map_var_val_it;

typedef vector<Check *> vec_chk;
typedef vector<Check *>::iterator vec_chk_it;
typedef map<Check*, msg> map_chk_val;
typedef map<Check*, msg>::iterator map_chk_val_it;

class Check {
public:
    int index;
    Check(int _index);
    vec_var vars;
    int add_variable(Variable *v);
    void send_messages();
};

class Variable {
public:
    int index;
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
void Check::send_messages() {
    // loop through each connected variable node
    for(vec_var_it i_it = this->vars.begin(); i_it != this->vars.end(); ++i_it) {
        Variable *v_target = *i_it;
        // loop through all *other* connected variable nodes
        msg msg_target = ZERO;
        for(vec_var_it j_it = this->vars.begin(); j_it != this->vars.end(); ++j_it) {
            Variable *v = *j_it;
            if(v_target = v) {
                continue;
            }
            msg v_value = v->value;
            if(v_value == ERASE) {
                msg_target = ERASE;
                break;
            }
            msg_target = (msg)((int)msg_target ^ (int)v_value);
            // outgoing message is sum%2 of incoming messages; any incoming erasure causes outgoing erasure
        }
        v_target->chks[this] = msg_target;
    }
        
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
}

msg Variable::update_value() {
    // determine current value of variable
    if(this->value == ERASE) {
        // read in all messages and apply variable node rules
        for(map_chk_val_it it = this->chks.begin(); it != this->chks.end(); ++it) {
            Check *c = it->first;
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

    Check* get_check(int index) {
        Check *c;
        int size = chks.size();
        if(index >= size) {
            chks.resize(index+1);
            for(int i = size; i <= index; i++) {
                chks[i] = new Check(i);
            }
        }
        c = chks[index];
        return c;
    }

    Variable* get_variable(int index) {
        Variable *v;
        int size = vars.size();
        if(index >= size) {
            vars.resize(index+1);
            for(int i = size; i <= index; i++) {
                vars[i] = new Variable(i);
            }
        }
        v = vars[index];
        return v;
    }

    int print_checks() {
        for(int i = 0; i < chks.size(); i++) {
            Check* c = chks[i];
            cout << "check " << i << ":";
            for(vec_var_it it = c->vars.begin(); it != c->vars.end(); ++it) {
                cout << " " << (*it)->index;
            }
            cout << endl;
        }
    }

    int print_variables() {
        for(int i = 0; i < vars.size(); i++) {
            Variable* v = vars[i];
            cout << "v" << i << ":";
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
    }

    int apply_channel(float p_e) {
        for(vec_var_it it = this->vars.begin(); it != this->vars.end(); ++it) {
            (*it)->apply_channel(p_e);
            DEBUG("v" << (*it)->index << " value: " << (*it)->value << endl);
        }
    }

    int decode(int iterations) {
        // TODO: only run BEC-SPA on undecoded variables
        // TODO: only run BEC-SPA on undecoded checks; connected vars can be removed
        // TODO: stop when no erasures remain

        // run check step

        for(vec_chk_it it = this->chks.begin(); it != this->chks.end(); ++it) {
            Check *c = *it;
            c->send_messages();
        }
        
        return 0;
    }
};


int main(int argc, char** argv) {

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
    g.print_checks();
    g.print_variables();
    g.apply_channel(0.35);
}


        //cout << "check " << c << " variables:" << endl;
        //copy(int_vars.begin(), int_vars.end(), ostream_iterator<int>(cout, " "));
