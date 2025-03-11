import os
import pickle
import tkinter as tk

import networkx as nx
import numpy as np
import pandas as pd
from networkx.drawing.nx_pydot import write_dot

from . import globals
from .util import imgrender, imgrender2, node_del_fixed, phase_relabel


class popupWindow9(object):
    def __init__(self, master, path):
        self.master = master
        self.path = path
        model_list_labels = [
            (str(path) + "/graph_theory_tests_" + str(i), i, "graph_theory_tests_" + str(i))
            for i in self.master.graph.nodes()
        ]
        #        model_list = []
        ref_wd = os.getcwd()
        base_cont_type = self.master.CONT_TYPE
        base_key_ref = self.master.key_ref
        base_context_no = self.master.CONTEXT_NO
        base_graph = self.master.graph
        base_chrono_graph = self.master.chrono_dag
        base_phi_ref = self.master.phi_ref
        base_prev_phase = self.master.prev_phase
        base_post_phase = self.master.post_phase
        base_context_no_unordered = self.master.context_no_unordered
        # RCD_EST = [int(list(self.master.datefile["date"])[list(self.master.datefile["context"]).index(i)]) for i in base_context_no]
        # RCD_ERR = [int(list(self.master.datefile["error"])[list(self.master.datefile["context"]).index(i)]) for i in base_context_no]
        # A = max(min(RCD_EST) - 4*max(RCD_EST), 0)
        # P = min(max(RCD_EST) + 4*max(RCD_EST), 50000)

        self.rc_llhds_dict = {}
        for i, j, k in model_list_labels:
            if k not in os.listdir(path):
                os.chdir(ref_wd)
                self.master.CONT_TYPE = base_cont_type.copy()
                self.master.key_ref = base_key_ref.copy()
                self.master.CONTEXT_NO = base_context_no.copy()
                self.master.graph = base_graph.copy()
                self.master.chrono_dag = base_chrono_graph.copy()
                self.master.phi_ref = base_phi_ref.copy()
                self.master.prev_phase = base_prev_phase.copy()
                self.master.post_phase = base_post_phase.copy()
                self.master.context_no_unordered = base_context_no_unordered.copy()
                # remove_node_section
                self.master.chrono_dag = node_del_fixed(self.master.chrono_dag, j)
                self.master.graph = node_del_fixed(self.master.graph, j)
                ref = np.where(np.array(base_context_no) == str(j))[0][0]
                ref2 = np.where(np.array(base_context_no_unordered) == str(j))[0][0]
                phase = self.master.key_ref[ref]
                phase_ref = np.where(np.array(base_phi_ref) == str(phase))[0][0]
                self.master.CONT_TYPE.pop(ref)
                self.master.key_ref.pop(ref)
                self.master.CONTEXT_NO.pop(ref)
                self.master.context_no_unordered.pop(ref2)
                ## ###correcting phases for removed nodes
                # change to new phase rels
                self.graph_adjust(phase, phase_ref)
                ######## sorting floating nodes
                group_conts = [self.master.CONTEXT_NO[i] for i, j in enumerate(self.master.key_ref) if j == phase]
                for m in group_conts:
                    if len(self.master.chrono_dag.out_edges(m)) == 0:
                        alph = [i for i in self.master.chrono_dag.nodes() if "a_" + phase in i]
                        self.master.chrono_dag.add_edge(m, alph[0], arrowhead="none")
                    if len(self.master.chrono_dag.in_edges(m)) == 0:
                        bet = [i for i in self.master.chrono_dag.nodes() if "b_" + phase in i]
                        self.master.chrono_dag.add_edge(bet[0], m, arrowhead="none")
                #############################    setting up the directorys
                dirs4 = self.make_directories(i)
                write_dot(self.master.chrono_dag, "fi_new_chrono")
                imgrender2(self.master.littlecanvas2.winfo_width(), self.master.littlecanvas2.winfo_height())
                imgrender(
                    self.master.graph, self.master.littlecanvas.winfo_width(), self.master.littlecanvas.winfo_height()
                )
                self.master.ACCEPT = [[]]
                while min([len(i) for i in self.master.ACCEPT]) < 20000:
                    (
                        self.master.CONTEXT_NO,
                        self.master.ACCEPT,
                        self.master.PHI_ACCEPT,
                        self.master.PHI_REF,
                        self.master.A,
                        self.master.P,
                        self.master.ALL_SAMPS_CONT,
                        self.master.ALL_SAMPS_PHI,
                        self.master.resultsdict,
                        self.master.all_results_dict,
                    ) = self.master.MCMC_func()
                globals.mcmc_check = "mcmc_loaded"
                self.save_state_1(self.master, dirs4)

    def prob_overlap(self, ll1, ll2):
        ### hellenger distance
        dist_probs = np.array([(np.sqrt(ll2[1][i]) - np.sqrt(j)) ** 2 for i, j in enumerate(ll1[1])])
        h = 1 - 1 / np.sqrt(2) * (np.sqrt(np.sum(dist_probs)))
        return h

    # def prob_from_samples(self, x_temp, A, P, lim=0.95, probs=0):
    #   if probs == 0:
    #       x_temp = np.array(x_temp)
    #       n = P - A + 1
    #       probs, x_vals = np.histogram(x_temp, range = (A, P), bins=n, density=1)
    #   df = pd.DataFrame({'Theta':x_vals[1:], 'Posterior':probs})
    #   y = df.sort_values(by=['Theta'], ascending=False)
    #   posterior_theta = np.array(y['Theta'])
    #   return posterior_theta

    def node_importance(self, graph):
        G = graph.to_undirected()  # setting up undirected graph
        df_prob_overlap = pd.concat(
            [
                pd.DataFrame(
                    [[str(i), str(j), self.prob_overlap(self.rc_llhds_dict[j], self.rc_llhds_dict[i])]],
                    columns=["node", "neighbour", "overlap_measure"],
                )
                for i in G.nodes()
                for j in list(G.neighbors(i))
            ]
        )
        # katz
        df_prob_overlap.to_csv("overlap_df.csv")
        dd = nx.pagerank(
            G, alpha=0.85, personalization=None, max_iter=100, tol=1e-06, nstart=None, weight="weight", dangling=None
        )
        df = pd.DataFrame.from_dict(dd, orient="index")
        df.reset_index(inplace=True)
        df.columns = ["context", "pagerank"]
        df.to_csv("katz_centr.csv")

    def graph_adjust(self, phase, phase_ref):
        graph_check = nx.transitive_reduction(self.master.chrono_dag)
        if self.master.chrono_dag.edges() != graph_check.edges():
            edges1 = list(self.master.chrono_dag.edges()).copy()
            for k in edges1:
                if k not in graph_check.edges():
                    self.master.chrono_dag.remove_edge(k[0], k[1])
        if phase not in self.master.key_ref:
            self.master.phi_ref.pop(phase_ref)
            if self.master.prev_phase[phase_ref] == "start":
                phase_node = [i for i in self.master.chrono_dag.nodes() if "b_" + str(phase) in i]
                self.master.chrono_dag.remove_node("a_" + str(phase))
                old_label = str(phase_node[0])
                new_label = "a_" + str(self.master.phi_ref[phase_ref + 1])
                mapping = {old_label: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.prev_phase[phase_ref] = "start"
            elif self.master.post_phase[phase_ref] == "end":
                phase_node = [i for i in self.master.chrono_dag.nodes() if "a_" + str(phase) in i]
                self.master.chrono_dag.remove_node("b_" + str(phase))
                old_label = str(phase_node[0])
                new_label = "b_" + str(self.master.phi_ref[phase_ref - 1])
                mapping = {old_label: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.post_phase[phase_ref] = "end"
            else:
                phase_nodes = [i for i in self.master.chrono_dag.nodes() if phase in i]
                self.master.chrono_dag.remove_edge(phase_nodes[0], phase_nodes[1])
                self.master.chrono_dag = nx.contracted_nodes(self.master.chrono_dag, phase_nodes[0], phase_nodes[1])
                new_label_1 = str(phase_nodes[0])
                new_label = new_label_1.replace("a_" + str(phase), "a_" + str(self.master.phi_ref[phase_ref + 1]))
                mapping = {phase_nodes[0]: new_label}
                self.master.prev_phase.pop(phase_ref)
                self.master.post_phase.pop(phase_ref)
                self.master.prev_phase[phase_ref] = "gap"
                self.master.post_phase[phase_ref] = "gap"
            self.master.chrono_dag = nx.relabel_nodes(self.master.chrono_dag, mapping)
            self.master.chrono_dag = phase_relabel(self.master.chrono_dag)
        self.master.chrono_dag.graph["graph"] = {"splines": "ortho"}
        atribs = nx.get_node_attributes(self.master.chrono_dag, "Group")
        nodes = self.master.chrono_dag.nodes()
        edge_add = []
        edge_remove = []
        for v, w in enumerate(self.master.CONTEXT_NO):
            ####find paths in that phase
            if self.master.CONT_TYPE[v] == "residual":
                phase = atribs[w]
                root = [i for i in nodes if "b_" + str(phase) in i][0]
                leaf = [i for i in nodes if "a_" + str(phase) in i][0]
                all_paths = []
                all_paths.extend(nx.all_simple_paths(self.master.chrono_dag, source=root, target=leaf))
                for f in all_paths:
                    ind = np.where(np.array(f) == str(w))[0][0]
                    edge_add.append((f[ind - 1], f[ind + 1]))
                for k in self.master.chrono_dag.edges():
                    if k[0] == w:
                        edge_remove.append((k[0], k[1]))
            elif self.master.CONT_TYPE[v] == "intrusive":
                for k in self.master.chrono_dag.edges():
                    if k[1] == w:
                        edge_remove.append((k[0], k[1]))
        for a in edge_add:
            self.master.chrono_dag.add_edge(a[0], a[1], arrowhead="none")
        for b in edge_remove:
            self.master.chrono_dag.remove_edge(b[0], b[1])

    def make_directories(self, i):
        dirs2 = os.path.join(i, "stratigraphic_graph")
        dirs3 = os.path.join(i, "chronological_graph")
        dirs4 = os.path.join(i, "python_only")
        dirs5 = os.path.join(i, "mcmc_results")
        os.makedirs(dirs2)
        os.makedirs(dirs3)
        os.makedirs(dirs4)
        os.makedirs(dirs5)
        os.chdir(i)
        return dirs4

    def selectall(self):
        self.e.select_set(0, "end")

    def save_state_1(self, master, j):
        vars_list_1 = dir(self.master)
        var_list = [
            var
            for var in vars_list_1
            if (("__" and "grid" and "get" and "tkinter" and "children") not in var) and (var[0] != "_")
        ]
        data = {}
        check_list = ["tkinter", "method", "__main__", "PIL"]
        for i in var_list:
            v = getattr(master, i)
            if not any(x in str(type(v)) for x in check_list):
                data[i] = v
        data["all_vars"] = list(data.keys())
        data["load_check"] = globals.load_check
        data["mcmc_check"] = globals.mcmc_check
        data["file_input"] = globals.FILE_INPUT
        path = j + "/save.pickle"
        if globals.mcmc_check == "mcmc_loaded":
            results = data["all_results_dict"]
            df = pd.DataFrame()
            for i in results.keys():
                df[i] = results[i][10000:]
            results_path = os.getcwd() + "/mcmc_results/full_results_df"
            df.to_csv(results_path)
            phasefile = data["phasefile"]
            context_no = data["CONTEXT_NO"]
            key_ref = [list(phasefile["Group"])[list(phasefile["context"]).index(i)] for i in context_no]
            df1 = pd.DataFrame(key_ref)
            df1.to_csv("mcmc_results/key_ref.csv")
            df2 = pd.DataFrame(context_no)
            df2.to_csv("mcmc_results/context_no.csv")

        try:
            with open(path, "wb") as f:
                pickle.dump(data, f)
        except Exception:
            tk.messagebox.showerror("Error", "File not saved")

    def load_cal_data(self, j):
        with open(self.path + "/" + str(j) + "/python_only/save.pickle", "rb") as f:
            data = pickle.load(f)
            vars_list = data["all_vars"]
            for i in vars_list:
                setattr(self, i, data[i])
            globals.FILE_INPUT = data["file_input"]
            globals.load_check = data["load_check"]
            globals.mcmc_check = data["mcmc_check"]
