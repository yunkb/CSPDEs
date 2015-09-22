from dolfin import *

class PiecewiseConstantDiffusionFEMModelML(FEMModel):
    
    def __init__(self, a, f, mesh_size):
        
        self.a         = a
        self.f         = f
        self.M_gen     = M_gen

        self.mesh_size = mesh_size
        self.init_simple_mesh()
        # I'm assuming, this is where we have to define the different regions... kinda annoying.

    def solve(self, z):
        # Make FEniCS output only the most important messages
        set_log_level(WARNING)

        # Create mesh if there is none
        if not hasattr(self, 'mesh'):
            self.init_simple_mesh()

        # Create approximation space
        V = FunctionSpace(self.mesh, 'Lagrange', degree=2)

        # Define boundary conditions
        bc = DirichletBC(V, Constant(0.0), lambda x, on_boundary: on_boundary)

        # Define variational problem
        w = TrialFunction(V)
        v = TestFunction(V)

        params = self.split_params([self.a, self.f], z)

        x = SpatialCoordinate(self.mesh)
        A = self.a(x, Constant(params[0])) * inner(nabla_grad(w), nabla_grad(v)) * dx
        L = self.f(x, Constant(params[1])) * v * dx

        # Create goal-functional for error estimation
        u      = Function(V)
        self.M = self.M_gen(self, u, dx)

        # Create solver
        problem     = LinearVariationalProblem(A, L, u, bc)
	self.solver = LinearVariationalSolver(problem)
	# y[k] = assemble(myAverage(mesh, u, dx))

        # Compute solution
        self.solver.solve()

        return u