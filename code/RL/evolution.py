import numpy as np
import random
import copy

MUTATION_RATE = 0.2

MUTATION_STRENGTH = 1.0

class EvolutionEngine:
    def __init__(self, population):
        self.population = population

    def evaluate_fitness(self):
        return [game.score for game in self.population]
    
    def select_parents(self, fitnesses):
        total = sum(fitnesses)
        probs = [f / total if total > 0 else 0 for f in fitnesses]
        parents = random.choices(self.population, weights=probs, k=2)
        return parents[0].agent.nn, parents[1].agent.nn

    def crossover(self, parent1, parent2):
        child = copy.deepcopy(parent1)
        for i in range(child.w1.shape[0]):
            for j in range(child.w1.shape[1]):
                child.w1[i][j] = random.choice([parent1.w1[i][j], parent2.w1[i][j]])
        for i in range(child.w2.shape[0]):
            for j in range(child.w2.shape[1]):
                child.w2[i][j] = random.choice([parent1.w2[i][j], parent2.w2[i][j]])
        return child
    
    def mutate(self, brain):
        for i in range(brain.w1.shape[0]):
            for j in range(brain.w1.shape[1]):
                if random.random() < MUTATION_RATE:
                    brain.w1[i][j] += np.random.randn() * MUTATION_STRENGTH
        for i in range(brain.w2.shape[0]):
            for j in range(brain.w2.shape[1]):
                if random.random() < MUTATION_RATE:
                    brain.w2[i][j] += np.random.randn() * MUTATION_STRENGTH
        return brain
    

    def next_generation(self):
        fitnesses = self.evaluate_fitness()
        new_agents = []

        best_idx = np.argmax(fitnesses)
        best_agent = copy.deepcopy(self.population[best_idx].agent)

        new_agents.append(best_agent)

        for _ in range(len(self.population) - 1):
            p1, p2 = self.select_parents(fitnesses)
            child_brain = self.crossover(p1, p2)
            mutated_brain = self.mutate(child_brain)
            
            new_agent = type(self.population[0].agent)()
            new_agent.nn = mutated_brain
            new_agents.append(new_agent)
        
        for i, game in enumerate(self.population):
            game.agent = new_agents[i]
            game.reset()
    
        
