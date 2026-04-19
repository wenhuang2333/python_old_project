"""
本次作业由小组共同完成
温煌 202440025344
黄仕昌202440025210
黎韦祥202440025218
本次作业使用源代码——sklearn库对照组共同建立起对数据分析的方法
"""



from collections import Counter

from nltk.classify.svm import SvmClassifier

class GaussianNaiveBayes:
    def __init__(self, epsilon=1e-8):
        self.classes = None
        self.mean = {}
        self.var = {}
        self.priors = {}
        self.epsilon = epsilon

    def fit(self, X, y):
        X = X.values if isinstance(X, pd.DataFrame) else X
        y = y.values if isinstance(y, pd.Series) else y

        self.classes = np.unique(y)
        n_samples = X.shape[0]

        # 计算每个类别的均值、方差和先验概率
        for c in self.classes:
            X_c = X[y == c]
            self.mean[c] = np.mean(X_c, axis=0)  # 各特征均值
            self.var[c] = np.var(X_c, axis=0)  # 各特征方差
            self.priors[c] = X_c.shape[0] / n_samples  # 先验概率

        return self

    def _calculate_log_likelihood(self, x, c):
        mean = self.mean[c]
        var = self.var[c] + self.epsilon  # 添加平滑项

        # 高斯分布的对数概率密度
        log_likelihood = -0.5 * np.sum(np.log(2 * np.pi * var))
        log_likelihood -= 0.5 * np.sum(((x - mean) ** 2) / var)

        return log_likelihood

    def predict_proba(self, X):
        X = X.values if isinstance(X, pd.DataFrame) else X
        n_samples = X.shape[0]
        n_classes = len(self.classes)

        probabilities = np.zeros((n_samples, n_classes))

        for i, x in enumerate(X):
            for j, c in enumerate(self.classes):
                # 计算对数先验概率
                log_prior = np.log(self.priors[c])
                # 计算对数似然
                log_likelihood = self._calculate_log_likelihood(x, c)
                # 计算对数后验概率
                log_posterior = log_prior + log_likelihood
                probabilities[i, j] = log_posterior

        probabilities = np.exp(probabilities - np.max(probabilities, axis=1, keepdims=True))
        probabilities = probabilities / np.sum(probabilities, axis=1, keepdims=True)
        return probabilities

    def predict(self, X):
        probabilities = self.predict_proba(X)
        return self.classes[np.argmax(probabilities, axis=1)]

    def score(self, X, y):
        y_pred = self.predict(X)
        y_true = y.values if isinstance(y, pd.Series) else y
        return np.mean(y_pred == y_true)



class KNNClf:
    def __init__(self, k=5):
        self.k = k
        self.y_labels = None

    def fit(self, X, y):
        self.X_train = X.values if isinstance(X, pd.DataFrame) else X
        self.y_train = y.values if isinstance(y, pd.Series) else y

        # 处理非数值型标签
        if not np.issubdtype(self.y_train.dtype, np.number):
            self.y_labels, self.y_train = np.unique(self.y_train, return_inverse=True)
        else:
            self.y_labels = None

        return self

    def euclidean_distance(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2) ** 2, axis=-1))

    def predict(self, X):
        # 转换输入数据类型
        X = X.values if isinstance(X, pd.DataFrame) else X

        # 对每个样本进行预测
        predictions = [self._predict(x) for x in X]

        # 如果有标签映射，则转换回原始标签
        if self.y_labels is not None:
            predictions = np.array([self.y_labels[p] for p in predictions])

        return np.array(predictions)

    def _predict(self, x):
        # 计算距离
        distances = self.euclidean_distance(x, self.X_train)

        # 获取最近的K个样本索引
        k_indices = np.argsort(distances)[:self.k]

        # 获取最近K个样本的标签
        k_labels = self.y_train[k_indices]

        most_common = Counter(k_labels).most_common(1)
        return most_common[0][0]

    def score(self, X, y):
        y_pred = self.predict(X)
        y_true = y.values if isinstance(y, pd.Series) else y
        return np.mean(y_pred == y_true)





class ManualDecisionTreeClassifier:
    class DecisionNode:
        def __init__(self, feature=None, value=None, true_branch=None, false_branch=None, prediction=None):
            self.feature = feature
            self.value = value
            self.true_branch = true_branch
            self.false_branch = false_branch
            self.prediction = prediction

    def __init__(self, criterion='gini', max_depth=None, random_state=None):
        self.root = None
        self.criterion = criterion
        self.max_depth = max_depth
        self.random_state = random_state
        if random_state is not None:
            np.random.seed(random_state)

    def entropy(self, labels):
        if len(labels) == 0:
            return 0
        counts = np.bincount(labels)
        probs = counts / len(labels)
        probs = probs[probs > 0]
        return -np.sum(probs * np.log2(probs))

    def gini(self, labels):
        if len(labels) == 0:
            return 0
        counts = np.bincount(labels)
        probs = counts / len(labels)
        return 1 - np.sum(probs ** 2)

    def impurity(self, labels):
        if self.criterion == 'gini':
            return self.gini(labels)
        else:
            return self.entropy(labels)

    def partition(self, data, labels, index, value):
        if isinstance(data, pd.DataFrame):
            data_array = data.values
        else:
            data_array = data

        mask = data_array[:, index] <= value
        left_data = data_array[mask]
        left_labels = labels[mask]
        right_data = data_array[~mask]
        right_labels = labels[~mask]

        if isinstance(data, pd.DataFrame):
            left_data = pd.DataFrame(left_data, columns=data.columns)
            right_data = pd.DataFrame(right_data, columns=data.columns)

        return left_data, left_labels, right_data, right_labels

    def info_gain(self, left_labels, right_labels, current_uncertainty):
        if len(left_labels) == 0 or len(right_labels) == 0:
            return 0
        p = len(left_labels) / (len(left_labels) + len(right_labels))
        return current_uncertainty - p * self.impurity(left_labels) - (1 - p) * self.impurity(right_labels)

    def find_best_split(self, data, labels, depth=0):
        if self.max_depth is not None and depth >= self.max_depth:
            return 0, None, None

        best_gain = 0
        best_index = None
        best_value = None
        current_uncertainty = self.impurity(labels)

        if isinstance(data, pd.DataFrame):
            data_array = data.values
        else:
            data_array = data

        n_features = data_array.shape[1]
        feature_indices = range(n_features)

        for index in feature_indices:
            values = np.unique(data_array[:, index])

            for value in values:
                left_data, left_labels, right_data, right_labels = self.partition(data, labels, index, value)

                if len(left_labels) == 0 or len(right_labels) == 0:
                    continue

                gain = self.info_gain(left_labels, right_labels, current_uncertainty)

                if gain > best_gain:
                    best_gain, best_index, best_value = gain, index, value

        return best_gain, best_index, best_value

    def build_tree(self, data, labels, depth=0):
        if len(np.unique(labels)) == 1:
            return self.DecisionNode(prediction=labels[0])

        best_gain, index, value = self.find_best_split(data, labels, depth)

        if best_gain <= 0 or index is None:
            return self.DecisionNode(prediction=Counter(labels).most_common(1)[0][0])

        left_data, left_labels, right_data, right_labels = self.partition(data, labels, index, value)
        true_branch = self.build_tree(left_data, left_labels, depth + 1)
        false_branch = self.build_tree(right_data, right_labels, depth + 1)

        return self.DecisionNode(feature=index, value=value, true_branch=true_branch, false_branch=false_branch)

    def fit(self, X, y):
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values
        y = y.astype(int)
        self.root = self.build_tree(X, y)

    def classify(self, row, node=None):
        if node is None:
            node = self.root
        if node.prediction is not None:
            return node.prediction
        if row[node.feature] <= node.value:
            return self.classify(row, node.true_branch)
        else:
            return self.classify(row, node.false_branch)

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.values
        return np.array([self.classify(row) for row in X])

    def score(self, X, y):
        y_pred = self.predict(X)
        if isinstance(y, pd.Series):
            y = y.values
        return np.mean(y_pred == y)


class ManualMLPClassifier:
    def __init__(self, hidden_layer_sizes, activation='relu', solver='adam', random_state=None):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        self.solver = solver
        self.random_state = random_state
        self.weights = []
        self.biases = []
        self.activations = []

    def fit(self, X, y):
        np.random.seed(self.random_state)
        X = np.array(X)
        y = np.array(y)

        if len(y.shape) == 1:
            y = self._one_hot_encode(y)

        layer_sizes = [X.shape[1]] + list(self.hidden_layer_sizes) + [y.shape[1]]
        self.activations = [self._get_activation_func(self.activation)] * (len(layer_sizes) - 2) + ['softmax']

        self.weights = []
        self.biases = []
        for i in range(len(layer_sizes) - 1):
            weight = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * 0.01
            bias = np.zeros((1, layer_sizes[i + 1]))
            self.weights.append(weight)
            self.biases.append(bias)

        if self.solver == 'adam':
            self._train_with_adam(X, y)
        else:
            self._train_with_sgd(X, y)

        return self

    def predict(self, X):
        X = np.array(X)
        probabilities = self._forward_propagation(X)
        return np.argmax(probabilities, axis=1)

    def score(self, X, y):
        X = np.array(X)
        y = np.array(y)
        predictions = self.predict(X)

        if len(y.shape) == 2:
            y = np.argmax(y, axis=1)

        return np.mean(predictions == y)

    def _forward_propagation(self, X):
        a = X
        for i in range(len(self.weights)):
            z = np.dot(a, self.weights[i]) + self.biases[i]

            if self.activations[i] == 'relu':
                a = np.maximum(0, z)
            elif self.activations[i] == 'logistic':
                a = 1 / (1 + np.exp(-z))
            elif self.activations[i] == 'tanh':
                a = np.tanh(z)
            elif self.activations[i] == 'softmax':
                exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
                a = exp_z / np.sum(exp_z, axis=1, keepdims=True)

        return a

    def _backward_propagation(self, X, y):
        m = X.shape[0]
        # 前向传播
        activations = [X]
        zs = []
        a = X

        for i in range(len(self.weights)):
            z = np.dot(a, self.weights[i]) + self.biases[i]
            zs.append(z)

            if self.activations[i] == 'relu':
                a = np.maximum(0, z)
            elif self.activations[i] == 'logistic':
                a = 1 / (1 + np.exp(-z))
            elif self.activations[i] == 'tanh':
                a = np.tanh(z)
            elif self.activations[i] == 'softmax':
                exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
                a = exp_z / np.sum(exp_z, axis=1, keepdims=True)

            activations.append(a)

        # 反向传播
        deltas = [activations[-1] - y]
        weight_gradients = []
        bias_gradients = []

        for i in reversed(range(len(self.weights))):
            # 计算权重和偏置的梯度
            weight_grad = np.dot(activations[i].T, deltas[-1]) / m
            bias_grad = np.sum(deltas[-1], axis=0, keepdims=True) / m

            weight_gradients.insert(0, weight_grad)
            bias_gradients.insert(0, bias_grad)

            if i > 0:  # 不是输入层
                if self.activations[i - 1] == 'relu':
                    derivative = np.array(zs[i - 1] > 0, dtype=np.float64)
                elif self.activations[i - 1] == 'logistic':
                    derivative = activations[i] * (1 - activations[i])
                elif self.activations[i - 1] == 'tanh':
                    derivative = 1 - np.power(activations[i], 2)

                delta = np.dot(deltas[-1], self.weights[i].T) * derivative
                deltas.append(delta)

        return weight_gradients, bias_gradients

    def _train_with_sgd(self, X, y, learning_rate=0.01, epochs=200):
        for epoch in range(epochs):
            weight_grads, bias_grads = self._backward_propagation(X, y)

            # 更新权重和偏置
            for i in range(len(self.weights)):
                self.weights[i] -= learning_rate * weight_grads[i]
                self.biases[i] -= learning_rate * bias_grads[i]

    def _train_with_adam(self, X, y, learning_rate=0.001, epochs=200,beta1=0.9, beta2=0.999, epsilon=1e-8):
        # 初始化Adam参数
        m_w = [np.zeros_like(w) for w in self.weights]
        v_w = [np.zeros_like(w) for w in self.weights]
        m_b = [np.zeros_like(b) for b in self.biases]
        v_b = [np.zeros_like(b) for b in self.biases]

        for epoch in range(epochs):
            weight_grads, bias_grads = self._backward_propagation(X, y)

            for i in range(len(self.weights)):
                # 更新权重的一阶矩和二阶矩估计
                m_w[i] = beta1 * m_w[i] + (1 - beta1) * weight_grads[i]
                v_w[i] = beta2 * v_w[i] + (1 - beta2) * (weight_grads[i] ** 2)

                # 修正偏差
                m_w_hat = m_w[i] / (1 - beta1 ** (epoch + 1))
                v_w_hat = v_w[i] / (1 - beta2 ** (epoch + 1))

                # 更新权重
                self.weights[i] -= learning_rate * m_w_hat / (np.sqrt(v_w_hat) + epsilon)

                # 更新偏置的一阶矩和二阶矩估计
                m_b[i] = beta1 * m_b[i] + (1 - beta1) * bias_grads[i]
                v_b[i] = beta2 * v_b[i] + (1 - beta2) * (bias_grads[i] ** 2)
                # 修正偏差
                m_b_hat = m_b[i] / (1 - beta1 ** (epoch + 1))
                v_b_hat = v_b[i] / (1 - beta2 ** (epoch + 1))
                # 更新偏置
                self.biases[i] -= learning_rate * m_b_hat / (np.sqrt(v_b_hat) + epsilon)

    def _one_hot_encode(self, y):
        classes = np.unique(y)
        n_classes = classes.size
        one_hot = np.zeros((y.size, n_classes))

        for i, label in enumerate(y):
            one_hot[i, np.where(classes == label)[0][0]] = 1

        return one_hot

    def _get_activation_func(self, activation):
        if activation == 'relu':
            return 'relu'
        elif activation == 'logistic' or activation == 'sigmoid':
            return 'logistic'
        elif activation == 'tanh':
            return 'tanh'
        else:  # 默认使用ReLU
            return 'relu'



from sklearn.metrics.pairwise import rbf_kernel, linear_kernel, polynomial_kernel
from sklearn.base import BaseEstimator, ClassifierMixin


class ManualSVC(BaseEstimator, ClassifierMixin):
    def __init__(self, C=1.0, kernel='rbf', gamma='scale', degree=3, coef0=0.0,max_iter=1000, tol=1e-3, learning_rate=0.01, probability=False):
        self.C = C
        self.kernel = kernel
        self.gamma = gamma
        self.degree = degree
        self.coef0 = coef0
        self.max_iter = max_iter
        self.tol = tol
        self.learning_rate = learning_rate
        self.probability = probability
        self.scaler = StandardScaler()
        self.classifiers = {}  # 存储所有二分类器
        self.classes_ = None
        self.n_classes = 0
        self.coef_ = None  # 特征系数
        self._probability_models = {}  # 存储概率估计模型

    def _preprocess_data(self, X):
        return self.scaler.fit_transform(X)

    def _compute_kernel(self, X, Y=None):
        if Y is None:
            Y = X


        if self.gamma == 'scale':
            gamma_val = 1.0 / (X.shape[1] * X.var())
        elif self.gamma == 'auto':
            gamma_val = 1.0 / X.shape[1]
        else:
            gamma_val = float(self.gamma)

        # 计算不同类型的核函数
        if self.kernel == 'linear':
            return np.dot(X, Y.T)
        elif self.kernel == 'poly':
            return (gamma_val * np.dot(X, Y.T) + self.coef0) ** self.degree
        elif self.kernel == 'rbf':
            pairwise_dists = np.sum(X ** 2, axis=1).reshape(-1, 1) + np.sum(Y ** 2, axis=1) - 2 * np.dot(X, Y.T)
            return np.exp(-gamma_val * pairwise_dists)

    def fit(self, X, y):
        X = self._preprocess_data(X)

        # 获取所有类别
        self.classes_ = np.unique(y)
        self.n_classes = len(self.classes_)
        n_features = X.shape[1]

        # 处理二分类情况
        if self.n_classes == 2:
            # 将标签转换为+1和-1
            y_binary = np.where(y == self.classes_[0], -1, 1)
            clf = self._train_binary_classifier(X, y_binary)
            self.classifiers[(self.classes_[0], self.classes_[1])] = clf

            self.coef_ = np.array([clf['w']])

            if self.probability:
                self._fit_probability_model(X, y_binary, clf)
        else:
            for i in range(self.n_classes):
                for j in range(i + 1, self.n_classes):
                    # 提取当前两个类别的样本
                    class_i = self.classes_[i]
                    class_j = self.classes_[j]
                    mask = (y == class_i) | (y == class_j)
                    X_ij = X[mask]
                    y_ij = y[mask]

                    # 将标签转换为+1和-1
                    y_ij_binary = np.where(y_ij == class_i, -1, 1)

                    # 训练二分类器
                    clf = self._train_binary_classifier(X_ij, y_ij_binary)

                    # 保存分类器和类别对
                    self.classifiers[(class_i, class_j)] = clf

            self.coef_ = np.zeros((self.n_classes, n_features))

            for (class_i, class_j), clf in self.classifiers.items():
                i_idx = np.where(self.classes_ == class_i)[0][0]
                j_idx = np.where(self.classes_ == class_j)[0][0]

                self.coef_[i_idx] -= clf['w']
                self.coef_[j_idx] += clf['w']

            if self.probability:
                self._fit_multiclass_probability_model(X, y)

        return self

    def _train_binary_classifier(self, X, y):
        n_samples, n_features = X.shape

        # 初始化权重和偏置
        w = np.zeros(n_features)
        b = 0

        # 梯度下降优化
        for iteration in range(self.max_iter):
            # 计算决策函数值
            margins = y * (np.dot(X, w) + b)

            # 计算梯度
            dw = np.zeros_like(w)
            db = 0

            # 遍历每个样本
            for i in range(n_samples):
                if margins[i] < 1:  # 违反约束的样本
                    dw += -y[i] * X[i]
                    db += -y[i]

            # 正则化项梯度
            dw = w + self.C * dw
            db = self.C * db

            w_prev = w.copy()
            w -= self.learning_rate * dw
            b -= self.learning_rate * db

            # 检查收敛
            if np.linalg.norm(w - w_prev) < self.tol:
                break

        return {'w': w, 'b': b}

    def _fit_probability_model(self, X, y, clf):
        from sklearn.linear_model import LogisticRegression

        decision_values = np.dot(X, clf['w']) + clf['b']

        lr = LogisticRegression()
        lr.fit(decision_values.reshape(-1, 1), (y + 1) // 2)  # 将-1/1转换为0/1

        self._probability_models[(self.classes_[0], self.classes_[1])] = lr

    def _fit_multiclass_probability_model(self, X, y):
        for (class_i, class_j), clf in self.classifiers.items():
            # 提取当前两个类别的样本
            mask = (y == class_i) | (y == class_j)
            X_ij = X[mask]
            y_ij = y[mask]
            y_ij_binary = np.where(y_ij == class_i, -1, 1)

            # 训练概率模型
            self._fit_probability_model(X_ij, y_ij_binary, clf)

    def decision_function(self, X):
        X = self.scaler.transform(X)
        n_samples = X.shape[0]

        # 二分类情况
        if self.n_classes == 2:
            class_i, class_j = self.classes_[0], self.classes_[1]
            clf = self.classifiers[(class_i, class_j)]
            return np.dot(X, clf['w']) + clf['b']
        # 多分类情况
        else:
            # 初始化投票矩阵
            votes = np.zeros((n_samples, self.n_classes))

            # 遍历所有二分类器
            for (class_i, class_j), clf in self.classifiers.items():
                i_idx = np.where(self.classes_ == class_i)[0][0]
                j_idx = np.where(self.classes_ == class_j)[0][0]

                # 计算决策函数值
                decision = np.dot(X, clf['w']) + clf['b']

                # 投票
                votes[decision > 0, j_idx] += 1
                votes[decision <= 0, i_idx] += 1

            return votes

    def predict(self, X):
        # 二分类情况
        if self.n_classes == 2:
            decision = self.decision_function(X)
            return np.where(decision > 0, self.classes_[1], self.classes_[0])
        # 多分类情况
        else:
            votes = self.decision_function(X)
            return self.classes_[np.argmax(votes, axis=1)]

    def predict_proba(self, X):
        if not self.probability:
            raise ValueError("probability 未启用，请在初始化时设置 probability=True")

        X = self.scaler.transform(X)
        n_samples = X.shape[0]

        # 二分类情况
        if self.n_classes == 2:
            class_i, class_j = self.classes_[0], self.classes_[1]
            clf = self.classifiers[(class_i, class_j)]
            decision_values = np.dot(X, clf['w']) + clf['b']
            lr = self._probability_models[(class_i, class_j)]
            proba = lr.predict_proba(decision_values.reshape(-1, 1))
            return proba
        # 多分类情况
        else:
            votes = self.decision_function(X)
            return votes / np.sum(votes, axis=1, keepdims=True)

    def score(self, X, y, **kwargs):
        y_pred = self.predict(X)
        return np.mean(y_pred == y)



class ManualKMeans:
    def __init__(self, n_clusters=8, init='random', n_init=10, max_iter=300, tol=1e-4, random_state=None):
        self.n_clusters = n_clusters
        self.init = init
        self.n_init = n_init
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.cluster_centers_ = None
        self.labels_ = None
        self.inertia_ = None

    def fit(self, X):
        X = np.array(X)
        n_samples, n_features = X.shape

        best_inertia = np.inf
        best_centers = None
        best_labels = None

        # 设置随机种子
        np.random.seed(self.random_state)

        # 多次运行算法，选择最优结果
        for _ in range(self.n_init):
            # 初始化中心点
            if self.init == 'random':
                # 随机选择初始中心点
                indices = np.random.choice(n_samples, self.n_clusters, replace=False)
                centers = X[indices]
            elif self.init == 'k-means++':
                # K-means++初始化方法
                centers = self._kmeans_plus_plus_init(X)

            # 迭代更新中心点
            for _ in range(self.max_iter):
                # 分配样本到最近的中心点
                labels = self._assign_labels(X, centers)

                # 更新中心点
                new_centers = self._update_centers(X, labels)

                # 检查收敛
                center_shift = np.sum(np.linalg.norm(new_centers - centers, axis=1))
                if center_shift < self.tol:
                    break

                centers = new_centers

            # 计算惯性（簇内误差平方和）
            inertia = self._compute_inertia(X, labels, centers)

            # 保存最优结果
            if inertia < best_inertia:
                best_inertia = inertia
                best_centers = centers
                best_labels = labels

        # 保存最优结果
        self.cluster_centers_ = best_centers
        self.labels_ = best_labels
        self.inertia_ = best_inertia

        return self

    def predict(self, X):
        X = np.array(X)
        return self._assign_labels(X, self.cluster_centers_)

    def _assign_labels(self, X, centers):
        distances = np.array([np.linalg.norm(X - center, axis=1) for center in centers])
        return np.argmin(distances, axis=0)

    def _update_centers(self, X, labels):
        centers = np.zeros((self.n_clusters, X.shape[1]))
        for i in range(self.n_clusters):
            cluster_points = X[labels == i]
            if len(cluster_points) > 0:
                centers[i] = np.mean(cluster_points, axis=0)
        return centers

    def _compute_inertia(self, X, labels, centers):
        inertia = 0
        for i in range(self.n_clusters):
            cluster_points = X[labels == i]
            inertia += np.sum(np.linalg.norm(cluster_points - centers[i], axis=1) ** 2)
        return inertia

    def _kmeans_plus_plus_init(self, X):
        n_samples, n_features = X.shape
        centers = np.zeros((self.n_clusters, n_features))
        centers[0] = X[np.random.randint(n_samples)]

        for i in range(1, self.n_clusters):
            # 计算每个样本到最近中心点的距离
            distances = np.array([np.min([np.linalg.norm(x - c) ** 2 for c in centers[:i]], axis=0) for x in X])

            # 根据距离的概率分布选择下一个中心点
            probs = distances / np.sum(distances)
            next_center_idx = np.random.choice(n_samples, p=probs)
            centers[i] = X[next_center_idx]

        return centers



class ManualPCA:
    def __init__(self, n_components=None, whiten=False, svd_solver='auto', random_state=None):
        self.n_components = n_components
        self.whiten = whiten
        self.svd_solver = svd_solver
        self.random_state = random_state

        # 存储PCA结果的属性
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        self.singular_values_ = None
        self.mean_ = None
        self.n_components_ = None
        self.noise_variance_ = None

    def fit(self, X):
        X = np.array(X, dtype=np.float64)
        n_samples, n_features = X.shape

        # 计算均值并中心化数据
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_

        # 选择SVD求解器
        if self.svd_solver == 'auto':
            if n_samples > n_features:
                solver = 'full'
            else:
                solver = 'arpack'
        else:
            solver = self.svd_solver

        # 执行SVD
        if solver == 'full':
            U, S, Vh = np.linalg.svd(X_centered, full_matrices=False)
            self.singular_values_ = S
        elif solver == 'arpack':
            from scipy.sparse.linalg import svds
            np.random.seed(self.random_state)
            U, S, Vh = svds(X_centered, k=self.n_components or n_features)
            self.singular_values_ = S[::-1]
            U = U[:, ::-1]
            Vh = Vh[::-1, :]
        else:
            raise ValueError(f"不支持的svd_solver: {self.svd_solver}")

        # 计算主成分
        self.components_ = Vh

        # 计算解释方差和方差比
        self.explained_variance_ = (self.singular_values_ ** 2) / (n_samples - 1)
        total_variance = np.sum(self.explained_variance_)
        self.explained_variance_ratio_ = self.explained_variance_ / total_variance

        # 确定实际使用的主成分数量
        if self.n_components is None:
            self.n_components_ = n_features
        else:
            self.n_components_ = min(self.n_components, n_features)
            self.components_ = self.components_[:self.n_components_]
            self.explained_variance_ = self.explained_variance_[:self.n_components_]
            self.explained_variance_ratio_ = self.explained_variance_ratio_[:self.n_components_]
            self.singular_values_ = self.singular_values_[:self.n_components_]

        # 计算噪声方差（仅当n_components < n_features时）
        if self.n_components_ < n_features:
            self.noise_variance_ = np.mean(self.explained_variance_[self.n_components_:])
        else:
            self.noise_variance_ = 0.0

        return self

    def transform(self, X):
        X = np.array(X, dtype=np.float64)
        X_centered = X - self.mean_

        # 计算主成分投影
        X_transformed = X_centered @ self.components_.T

        # 白化处理
        if self.whiten:
            X_transformed = X_transformed / np.sqrt(self.explained_variance_ + 1e-10)

        return X_transformed

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)




import numba as nb
from sklearn.neighbors import BallTree, KDTree
@nb.njit(parallel=True, fastmath=True)
def compute_core_points(X, eps, min_samples):
    n_samples, n_features = X.shape
    core_points = np.zeros(n_samples, dtype=np.bool_)
    neighbor_counts = np.zeros(n_samples, dtype=np.int32)

    # 并行计算每个点的邻域点数量
    for i in nb.prange(n_samples):
        count = 0
        for j in range(n_samples):
            if i == j:
                continue
            dist = 0.0
            for d in range(n_features):
                dist += (X[i, d] - X[j, d]) ** 2
            if np.sqrt(dist) <= eps:
                count += 1
        neighbor_counts[i] = count
        core_points[i] = (count >= min_samples)

    return core_points, neighbor_counts


@nb.njit(fastmath=True)
def expand_cluster(X, core_points, neighbor_counts, labels, core_neighbors, current_cluster, i, eps):
    """扩展聚类（Numba优化版本）"""
    n_samples, n_features = X.shape
    seeds = [i]
    labels[i] = current_cluster

    seed_index = 0
    while seed_index < len(seeds):
        current_point = seeds[seed_index]

        # 获取当前点的邻域
        neighbors = []
        for j in range(n_samples):
            if j == current_point:
                continue
            dist = 0.0
            for d in range(n_features):
                dist += (X[current_point, d] - X[j, d]) ** 2
            if np.sqrt(dist) <= eps:
                neighbors.append(j)

        # 如果是核心点，处理其邻域点
        if core_points[current_point]:
            for neighbor in neighbors:
                if labels[neighbor] == -1:  # 未分类
                    labels[neighbor] = current_cluster
                    if core_points[neighbor]:
                        seeds.append(neighbor)
        seed_index += 1


class ManualDBSCAN:
    def __init__(self, eps=0.5, min_samples=5, algorithm='auto', leaf_size=30, n_jobs=None):
        self.eps = eps
        self.min_samples = min_samples
        self.algorithm = algorithm
        self.leaf_size = leaf_size
        self.n_jobs = n_jobs
        self.labels_ = None
        self.core_sample_indices_ = None

    def fit(self, X):
        X = np.ascontiguousarray(X)
        n_samples, n_features = X.shape

        # 初始化标签为-1（未分类）
        self.labels_ = np.full(n_samples, -1, dtype=np.int32)

        # 选择合适的近邻搜索算法
        if self.algorithm == 'auto':
            if n_features > 10:
                self.algorithm = 'ball_tree'
            else:
                self.algorithm = 'kd_tree'

        # 计算核心点
        if self.algorithm in ['ball_tree', 'kd_tree']:
            # 使用树结构加速
            if self.algorithm == 'ball_tree':
                tree = BallTree(X, leaf_size=self.leaf_size)
            else:
                tree = KDTree(X, leaf_size=self.leaf_size)

            # 查询每个点的eps邻域
            neighbor_indices = tree.query_radius(X, r=self.eps, return_distance=False)

            # 标记核心点
            core_points = np.array([len(neighbors) >= self.min_samples for neighbors in neighbor_indices])
            self.core_sample_indices_ = np.where(core_points)[0]

            # 构建核心点邻接表
            core_neighbors = {}
            for i in self.core_sample_indices_:
                core_neighbors[i] = [j for j in neighbor_indices[i] if core_points[j]]
        else:
            # 使用Numba优化的暴力计算方法
            core_points, _ = compute_core_points(X, self.eps, self.min_samples)
            self.core_sample_indices_ = np.where(core_points)[0]

        # 聚类过程
        current_cluster = 0
        for i in self.core_sample_indices_:
            if self.labels_[i] == -1:  # 未分类
                expand_cluster(X, core_points, None, self.labels_, None, current_cluster, i, self.eps)
                current_cluster += 1

        return self


class ManualVarianceThreshold:
    def __init__(self, threshold=0.0):
        self.threshold = threshold
        self.variances = None
        self.support = None

    def fit(self, X):
        # 确保输入是NumPy数组
        if isinstance(X, pd.DataFrame):
            X = X.values

        # 计算每个特征的方差
        self.variances = np.var(X, axis=0)

        # 确定哪些特征的方差大于阈值
        self.support = self.variances > self.threshold

        return self

    def transform(self, X):
        # 确保输入是NumPy数组
        if isinstance(X, pd.DataFrame):
            X_values = X.values
            # 应用特征选择
            X_selected = X_values[:, self.support]
            # 如果输入是DataFrame，返回DataFrame
            return pd.DataFrame(X_selected, columns=X.columns[self.support])
        else:
            # 如果输入是NumPy数组，返回NumPy数组
            return X[:, self.support]

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

    def get_support(self):
        return self.support


from scipy import stats
def Manualf_classif(X, y):
    classes = np.unique(y)
    n_classes = len(classes)

    n_samples, n_features = X.shape
    f_values = np.zeros(n_features)
    p_values = np.zeros(n_features)

    for i in range(n_features):
        feature_values = X[:, i]
        group_values = [feature_values[y == c] for c in classes]

        # 计算组内和组间方差
        group_means = [np.mean(g) for g in group_values]
        overall_mean = np.mean(feature_values)

        # 组间平方和 (SSB)
        ssb = 0
        for j, g in enumerate(group_values):
            ssb += len(g) * (group_means[j] - overall_mean) ** 2

        # 组内平方和 (SSW)
        ssw = 0
        for g in group_values:
            ssw += np.sum((g - np.mean(g)) ** 2)
        df_between = n_classes - 1
        df_within = n_samples - n_classes

        # F值
        if ssw == 0:
            f_values[i] = 0
        else:
            f_values[i] = (ssb / df_between) / (ssw / df_within)

        # p值 (使用F分布)
        p_values[i] = stats.f.sf(f_values[i], df_between, df_within)

    return f_values, p_values





#  绘图库
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
mpl.rcParams.update(mpl.rcParamsDefault)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
#作用：修复 matplotlib 负号显示为方框的问题（常见于中文系统环境）
import warnings
warnings.filterwarnings(action='ignore') #全局忽略 Python 的警告信息（如函数弃用提示），避免输出干扰
from sklearn.metrics import confusion_matrix, f1_score
#confusion_matrix：生成分类结果混淆矩阵
#f1_score：计算 F1 值（精确率与召回率的调和平均）
#roc_curve/auc：绘制 ROC 曲线并计算 AUC 值
#precision_recall_curve：绘制精确率-召回率曲线
#accuracy_score：计算分类准确率

#train_test_split：拆分数据集为训练集和测试集
#KFold：K折交叉验证
#LeaveOneOut/LeavePOut：留一法/留P法交叉验证
#cross_val_score/cross_validate：自动化交叉验证评分


from sklearn import neighbors # K近邻算法（分类/回归）
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score,train_test_split
from sklearn import tree
from sklearn.svm import SVC
from pylab import *
from sklearn.feature_selection import VarianceThreshold,SelectKBest,f_classif,chi2
from sklearn.feature_selection import RFE,RFECV,SelectFromModel
from sklearn.linear_model import enet_path,ElasticNetCV,ElasticNet
from sklearn.cluster import KMeans, AgglomerativeClustering, affinity_propagation
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2
from sklearn.cluster import DBSCAN,Birch,KMeans,estimate_bandwidth,MeanShift
from sklearn import ensemble
from sklearn.metrics import accuracy_score
from flask import Flask,request,jsonify,render_template,redirect, url_for,flash,session
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.metrics import calinski_harabasz_score
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import jaccard_score, fowlkes_mallows_score, rand_score, adjusted_rand_score, normalized_mutual_info_score
#创建flask对象
app=Flask(__name__)
app.secret_key = 'your_secret_key'
ALLOW={'csv','xls','xlsx'}
print("初次启动可能会有些卡顿，如果一直没进行请重新启动。")

all_data={}
def is_single(col):
    uniq=col.unique()
    uninum=len(col)

    if uninum<=int(len(col)*0.5):
        return False
    else:
        return True
def remath_single(col):
    utype=set()
    for i in range(0,len(col)):
        utype.add(col[i])
    utype=list(utype)
    udict={}
    for i in range(0,len(utype)):
        udict[utype[i]]=i
    for i in range(0,len(col)):
        col[i]=int(udict[col[i]])
    return col
def pre_doing(data):
    # imputer = SimpleImputer(strategy='mean')
    # data=imputer.fit_transform(data)
    data=data.dropna()
    cols = data.columns.tolist()
    cols_to_drop = []
    for col_name in cols:
        if data[col_name].dtype == 'object':
            some_data = set(data[col_name])
            Sdata = {value: i for i, value in enumerate(some_data)}
            data[col_name] = data[col_name].map(Sdata)
            if not is_single(data[col_name]):
                print(col_name)
                cols_to_drop.append(col_name)

    data = data.drop(columns=cols_to_drop)
    for col_name in data.columns:
        if data[col_name].dtype == 'datetime64[ns]':
            data[col_name] = data[col_name].astype(int) / 10**9
    scaler = StandardScaler()
    data = scaler.fit_transform(data)
    data=pd.DataFrame(data)

    return data
def from_river_to_the_sea(confusion):
    ans="<br>["
    for i in range(0,len(confusion)):
        ans+="["
        for j in range(0,len(confusion[i])):
            ans+=str(confusion[i][j])
            ans+=","
        ans=ans[:-1]
        ans+="]<br>"
    ans=ans[:-4]
    ans+="]"
    return ans

f=[]

#——————————————————————————————————————此处开始是源代码————————————————————
def BYS(data,destination):
    data=data.dropna()
    destination=int(destination)
    answer=[]
    modelNB=GaussianNaiveBayes()
    y=data.iloc[:,destination]
    y=remath_single(y)
    x=data.drop(columns=data.columns[destination])
    x0,x1,y0,y1=train_test_split(x,y,test_size=0.75,random_state=42)
    modelNB.fit(x0,y0)
    y2=modelNB.predict(x1)
    answer.append(accuracy_score(y1,y2))#准确率
    answer.append(precision_score(y1,y2, average='weighted'))#精确率
    answer.append(recall_score(y1,y2, average='weighted'))#召回率
    answer.append(f1_score(y1,y2, average='weighted'))#F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1,y2)))#混淆矩阵
    answer.append(1-modelNB.score(x0, y0))
    answer.append(1-modelNB.score(x1, y1))

    # y_score=modelNB.predict_proba(x1)[:,1]
    # fpr,tpr,th=roc_curve(y1,y_score)
    # roc_auc=auc(fpr,tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'BYS_img.png')
    # plt.savefig(image_path)
    # plt.close()
    print("贝叶斯分类器工作完成")
    return answer

#此处有源代码
def K_neighbor(data,destination,K):
    data = data.dropna()
    destination = int(destination)
    answer = []
    K=int(K)
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=42)
    modelKNN=KNNClf(k=K)
    modelKNN.fit(x0,y0)
    y2=modelKNN.predict(x1)
    answer.append(accuracy_score(y1, y2))  # 准确率
    answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
    answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
    answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
    answer.append(1-modelKNN.score(x0, y0))
    answer.append(1-modelKNN.score(x1, y1))

    # y_score = modelKNN.predict_proba(x1)[:, 1]
    # fpr, tpr, th = roc_curve(y1, y_score)
    # roc_auc = auc(fpr, tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'KNN_img.png')
    # plt.savefig(image_path)
    # plt.close()

    print("KNN分类器工作完成")
    return answer

#此处有源代码
def decision_tree(data,destination,deep):
    data=data.dropna()
    destination=int(destination)
    answer = []
    deep=int(deep)
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=123)

    modelDTC=ManualDecisionTreeClassifier(criterion='gini', max_depth=deep, random_state=42)
    modelDTC.fit(x0,y0)
    y2=modelDTC.predict(x1)
    answer.append(accuracy_score(y1, y2))  # 准确率
    answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
    answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
    answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
    answer.append(1-modelDTC.score(x0, y0))
    answer.append(1-modelDTC.score(x1, y1))

    # y_score = modelDTC.predict_proba(x1)[:, 1]
    # fpr, tpr, th = roc_curve(y1, y_score)
    # roc_auc = auc(fpr, tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'DTC_img.png')
    # plt.savefig(image_path)
    # plt.close()

    print("决策树分类器工作完成")
    return answer

def together_learn(data,destination,type_learn,num,deep):
    data = data.dropna()
    destination = int(destination)
    answer = []
    num=int(num)
    deep = int(deep)
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=123)
    if type_learn=="RandomForestClassifier":
        clf = RandomForestClassifier(n_estimators=num, criterion='gini', max_depth=deep, random_state=42)
        clf.fit(x0,y0)
        y2=clf.predict(x1)
        answer.append(accuracy_score(y1, y2))  # 准确率
        answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
        answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
        answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
        answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
        answer.append(1-clf.score(x0, y0))
        answer.append(1-clf.score(x1, y1))

        # y_score = clf.predict_proba(x1)[:, 1]
        # fpr, tpr, th = roc_curve(y1, y_score)
        # roc_auc = auc(fpr, tpr)
        # plt.figure()
        # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
        # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        # plt.xlim([0.0, 1.0])
        # plt.ylim([0.0, 1.05])
        # plt.xlabel('False Positive Rate')
        # plt.ylabel('True Positive Rate')
        # plt.title('Receiver Operating Characteristic')
        # plt.legend(loc="lower right")
        # static_dir = os.path.join(os.path.dirname(__file__), 'static')
        # if not os.path.exists(static_dir):
        #     os.makedirs(static_dir)
        # image_path = os.path.join(static_dir, 'clf_img.png')
        # plt.savefig(image_path)
        # plt.close()

        print("集成学习分类器工作完成")
        return answer
    else:
        clf = GradientBoostingClassifier(n_estimators=num, learning_rate=0.1, max_depth=deep, random_state=42)
        clf.fit(x0, y0)
        y2 = clf.predict(x1)
        answer.append(accuracy_score(y1, y2))  # 准确率
        answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
        answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
        answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
        answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
        answer.append(1-clf.score(x0,y0))
        answer.append(1-clf.score(x1, y1))

        # y_score = clf.predict_proba(x1)[:, 1]
        # fpr, tpr, th = roc_curve(y1, y_score)
        # roc_auc = auc(fpr, tpr)
        # plt.figure()
        # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
        # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        # plt.xlim([0.0, 1.0])
        # plt.ylim([0.0, 1.05])
        # plt.xlabel('False Positive Rate')
        # plt.ylabel('True Positive Rate')
        # plt.title('Receiver Operating Characteristic')
        # plt.legend(loc="lower right")
        # static_dir = os.path.join(os.path.dirname(__file__), 'static')
        # if not os.path.exists(static_dir):
        #     os.makedirs(static_dir)
        # image_path = os.path.join(static_dir, 'clf_img.png')
        # plt.savefig(image_path)
        # plt.close()
        print("集成学习分类器工作完成")
        return answer

# 此处有源代码
def netMLP(data,destination,num,func,you):
    data = data.dropna()
    destination = int(destination)
    answer = []
    num=tuple(num)
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=123)
    NeuNet=ManualMLPClassifier(hidden_layer_sizes=num, activation=func, solver=you, random_state=42)
    NeuNet.fit(x0,y0)
    y2=NeuNet.predict(x1)
    answer.append(accuracy_score(y1, y2))  # 准确率
    answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
    answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
    answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
    answer.append(1-NeuNet.score(x0, y0))
    answer.append(1-NeuNet.score(x1, y1))

    # y_score = NeuNet.predict_proba(x1)[:, 1]
    # fpr, tpr, th = roc_curve(y1, y_score)
    # roc_auc = auc(fpr, tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'net_img.png')
    # plt.savefig(image_path)
    # plt.close()

    print("人工神经网络分类器工作完成")
    return answer

#此处有源代码
def SVC_(data,destination,C,type,pro):
    data = data.dropna()
    destination = int(destination)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=42)
    svc=ManualSVC(C=C,kernel=type,probability=pro)
    svc.fit(x0,y0)
    y2=svc.predict(x1)
    answer.append(accuracy_score(y1, y2))  # 准确率
    answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
    answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
    answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
    answer.append(1 - svc.score(x0, y0))
    answer.append(1 - svc.score(x1, y1))

    # y_score = svc.predict_proba(x1)[:, 1]
    # fpr, tpr, th = roc_curve(y1, y_score)
    # roc_auc = auc(fpr, tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'svc_img.png')
    # plt.savefig(image_path)
    # plt.close()

    print("支持向量机分类器工作完成")
    return answer

#此处有源代码
def VT(data,goal,threshold,dataq):
    data = data.dropna()
    destination = int(goal)
    threshold=float(threshold)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    xx=dataq.drop(columns=dataq.columns[destination])
    selector=ManualVarianceThreshold(threshold=threshold)
    X=selector.fit_transform(x)
    X=pd.DataFrame(X)
    y=pd.DataFrame(y)
    answer.append(X)
    answer.append(y)
    answer.append(x.columns.tolist())
    answer.append(x.var().to_dict())
    answer.append(selector.get_support())
    answer.append(X.shape[1])
    print("过滤式策略下的低方差选择特征完成")
    return answer
from sklearn import __version__ as sklearn_version
#此处有部分源代码
def SK(data,goal,func,threshold,dataq):
    data = data.dropna()
    destination = int(goal)
    threshold = int(threshold)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    xx = dataq.drop(columns=dataq.columns[destination])
    selector = SelectKBest(score_func=Manualf_classif, k=threshold)
    if func=='f_classif':
        pass
    elif func=='chi2':
        selector = SelectKBest(score_func=chi2, k=threshold)
    elif func=='mutual_info_classif':
        selector = SelectKBest(score_func=mutual_info_classif, k=threshold)
    elif func=='f_regression':
        selector = SelectKBest(score_func=f_regression, k=threshold)
    elif func=='mutual_info_regression':
        selector = SelectKBest(score_func=mutual_info_regression, k=threshold)
    X = selector.fit_transform(x,y)
    X = pd.DataFrame(X)
    y = pd.DataFrame(y)
    # 查看选择的特征
    # print("\n选择后的特征：")
    # print(X[:5])  # 打印前5行
    # # 查看每个特征的评分
    # print("\n特征评分：")
    # print(selector.scores_)
    # # # 查看哪些特征被选中
    # # print("\n被选中的特征：")
    # # print(selector.support_)
    # # # 查看特征排名
    # # print("\n特征排名：")
    # # print(selector.ranking_)
    # # 查看每个特征的p值
    # print("\n特征的p值：")
    # print(selector.pvalues_)
    answer.append(X)
    answer.append(y)
    answer.append(selector.scores_)
    answer.append(selector.pvalues_)
    answer.append(selector.get_support())#布尔掩码
    print("过滤式策略下的高相关选择特征完成")
    return answer

#此处有部分源代码
def RFE_(data,goal,num,obj,step):
    data = data.dropna()
    destination = int(goal)
    num=int(num)
    step=int(step)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    estimator = ManualSVC(kernel="linear")
    if obj=="SVM":
        pass
    elif obj=="Logistic Regression":
        estimator = LogisticRegression(max_iter=1000)
    elif obj=="Linear Regression":
        estimator = LinearRegression()
    elif obj=="Ridge Regression":
        estimator = Ridge(alpha=1.0)
    elif obj=="Decision Tree":
        estimator = DecisionTreeClassifier()
    elif obj=="Lasso":
        estimator = Lasso(alpha=0.1)
    elif obj=="Gradient Boosting":
        estimator = GradientBoostingClassifier(n_estimators=100)
    elif obj=="Random Forest":
        estimator = RandomForestClassifier(n_estimators=100)
    elif obj=="LDA":
        estimator = LinearDiscriminantAnalysis()
    selector=RFE(estimator=estimator,n_features_to_select=num,step=step)
    selector.fit(x,y)
    # print("保留的特征：", selector.support_)
    # print("特征排名：", selector.ranking_)
    X=selector.transform(x)
    X=pd.DataFrame(X)
    y=pd.DataFrame(y)
    answer.append(X)
    answer.append(y)
    answer.append(selector.support_)
    answer.append(selector.ranking_)
    print("包裹式特征选择策略完成")
    return answer

def Lasso_(data,goal,num,round,tol,ni,dataq):
    data = data.dropna()
    destination = int(goal)
    num = float(num)
    round=int(round)
    tol=float(tol)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x = pd.DataFrame(x)
    y = pd.DataFrame(y)
    dataqq = dataq.drop(columns=dataq.columns[goal])
    x.columns=dataqq.columns.tolist()
    y.columns = [dataq.columns.tolist()[goal]]
    lasso=Lasso(alpha=num,max_iter=round,tol=tol,fit_intercept=ni,random_state=42)
    lasso.fit(x,y)
    # print("特征系数:", {k: float(v) for k, v in dict(zip(x.columns, lasso.coef_)).items()})
    # print("截距项：", lasso.intercept_)
    # print("被淘汰的特征:", x.columns[lasso.coef_ == 0])
    key=[]
    for k,v in dict(zip(x.columns, lasso.coef_)).items():
        if v<=0:
            continue
        else:
            key.append(k)
    off=x.columns[lasso.coef_ == 0]
    character={k:float(v) for k,v in dict(zip(x.columns, lasso.coef_)).items()}
    x=x[key]
    answer.append(x)
    answer.append(y)
    answer.append(character)
    answer.append(lasso.intercept_)
    answer.append(off)
    answer.append(key)
    print("基于Lasso回归的嵌入式特征选择策略完成")
    return answer

def ridge(data,goal,num,round,tol,ni,gui,dataq,limit):
    data = data.dropna()
    destination = int(goal)
    num = float(num)
    round = int(round)
    tol = float(tol)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    scaler = StandardScaler()
    if gui:
        x=scaler.fit_transform(x)
    x = pd.DataFrame(x)
    y = pd.DataFrame(y)
    dataqq = dataq.drop(columns=dataq.columns[goal])
    x.columns = dataqq.columns.tolist()
    y.columns = [dataq.columns.tolist()[goal]]
    ridge=Ridge(alpha=num,max_iter=round,tol=tol,fit_intercept=ni,random_state=42)
    ridge.fit(x,y)
    # print("特征系数：", ridge.coef_)
    # print("截距项：", ridge.intercept_)
    absf=abs(ridge.coef_)
    un=np.where(absf<limit)[0]
    final=[]
    not_final=[]
    # print("absf:",absf)
    # print("absf的形状:",absf.shape)
    # print("absf的类型：",absf.dtype)
    # print()
    for i in range(0,len(absf)):
        # print("当前是",dataq.columns.tolist()[i],"un[i]:",absf[i],";","limit:",limit)
        if absf[i]<limit:
            not_final.append(dataq.columns.tolist()[i])
        else:
            final.append(i)
    x=x.iloc[:,final]
    # print(x)
    # print(not_final)
    answer.append(x)
    answer.append(y)
    answer.append(ridge.coef_)
    answer.append(ridge.intercept_)
    answer.append(not_final)
    print("基于岭回归的嵌入式特征选择策略完成")
    return answer

def elastic(data,goal,num,round,L1,tol,ni,gui,dataq,limit):
    data = data.dropna()
    destination = int(goal)
    num = float(num)
    round = int(round)
    tol = float(tol)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    scaler = StandardScaler()
    if gui:
        x = scaler.fit_transform(x)
    x = pd.DataFrame(x)
    y = pd.DataFrame(y)
    dataqq = dataq.drop(columns=dataq.columns[goal])
    x.columns = dataqq.columns.tolist()
    y.columns = [dataq.columns.tolist()[goal]]
    elastic_net=ElasticNet(alpha=num,max_iter=round,l1_ratio=L1,tol=tol,fit_intercept=ni,random_state=42)
    elastic_net.fit(x,y)
    key=[]
    final=[]
    not_final=[]
    actual={}
    for i in range(0,len(dataqq.columns.tolist())):
        actual[dataqq.columns.tolist()[i]]=elastic_net.coef_[i]
        if abs(elastic_net.coef_[i])<limit:
            not_final.append(dataqq.columns.tolist()[i])
        else:
            key.append(i)
            final.append(dataqq.columns.tolist()[i])
    x=x.iloc[:,key]
    print("特征系数：", elastic_net.coef_)
    print("截距项：", elastic_net.intercept_)
    print("实际迭代次数：", elastic_net.n_iter_)
    answer.append(x)
    answer.append(y)
    answer.append(final)#被选中的
    answer.append(not_final)#被筛选的
    answer.append(actual)#各个特征的特征系数
    answer.append(elastic_net.intercept_)#截距项
    answer.append(elastic_net.n_iter_)#迭代次数
    print("基于弹性网的嵌入式特征选择策略完成")
    return answer

#此处有源代码
def PCA_(data,aim,num,white,solve,dataq):
    data = data.dropna()
    destination = int(aim)
    num = int(num)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x = pd.DataFrame(x)

    y = pd.DataFrame(y)
    dataqq = dataq.drop(columns=dataq.columns[destination])
    x.columns = dataqq.columns.tolist()
    y.columns = [dataq.columns.tolist()[destination]]
    print(x)
    pca=ManualPCA(n_components=num,whiten=white,svd_solver=solve,random_state=42)
    pca.fit(x)
    # print("2主成分的权重向量:", pca.components_)
    # print("3每个主成分所解释的方差大小", pca.explained_variance_)
    # print("4每个主成分所解释的方差占总方差的比例:", pca.explained_variance_ratio_)
    # print("5奇异值:", pca.singular_values_)
    # print("6数据的均值:", pca.mean_)
    # print("7实际保留的主成分数量:", pca.n_components_)
    # print("8噪声的方差:", pca.noise_variance_)
    X=pca.fit_transform(x)
    X=pd.DataFrame(X)

    answer.append(X)
    answer.append(y)
    answer.append(pca.components_)
    answer.append(pca.explained_variance_)
    answer.append(pca.explained_variance_ratio_)
    answer.append(pca.singular_values_)
    answer.append(pca.mean_)
    answer.append(pca.n_components_)
    answer.append(pca.noise_variance_)


    # plt.figure(figsize=(8, 6))
    # plt.scatter(X[:, 0], X[:, 1], alpha=0.5, label='原始数据点')
    # plt.scatter(X_pca, np.zeros_like(X_pca), c='red', alpha=0.5, label='筛选后的主成分数据')
    # plt.xlabel('Feature 1')
    # plt.ylabel('Feature 2')
    # plt.title('PCA 数据降维可视化')
    # plt.legend()
    # plt.grid(True)


    print("主成分分析完成")
    return answer

#此处有源代码
def KN_cluster(data,first,second,num,func,seed,d,tol):
    y=data.iloc[:,-1]
    y=pd.DataFrame(y)
    data = data.drop(data.columns[-1], axis=1)
    kmeans = ManualKMeans(n_clusters=num, init=func, n_init=seed, max_iter=d, tol=tol, random_state=42)
    kmeans.fit(data)
    type1_=set()
    for i in range(0,y.shape[0]):
        type1_.add(y.iloc[i,0])
    type1=list(type1_)
    type2={}
    for i in range(0,len(type1_)):
        type2[type1[i]]=i
    for i in range(0,y.shape[0]):
        y.iloc[i,0]=type2[y.iloc[i,0]]
    y=y.astype(int)
    data['cluster']=kmeans.labels_
    data['destination']=y
    name=data.columns.tolist()
    fig = plt.figure(figsize=(12, 8))
    plt.subplot(121)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[3]], cmap='viridis', label=f'真实的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"以{name[0]}和{name[1]}为参考特征的、以{name[2]}为目标变量的K聚类结果:真实分类")
    plt.legend()

    # 第二个子图：预测的分类
    plt.subplot(122)
    plt.scatter(data[name[0]], data[name[1]], c=kmeans.labels_, cmap='viridis', label=f'预测的{name[2]}分类')
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=100, c='red', marker='X',
                label='聚类中心')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"预测分类")
    plt.legend()
    plt.savefig('./static/KN.png', dpi=300, bbox_inches='tight', transparent=True)
    answer=[]
    labels=kmeans.labels_
    y = y.iloc[:, 0].values
    answer.append(silhouette_score(data[[name[0], name[1]]], kmeans.labels_))#0
    answer.append(calinski_harabasz_score(data[[name[0], name[1]]], kmeans.labels_))#1
    answer.append(davies_bouldin_score(data[[name[0], name[1]]], kmeans.labels_))#2
    answer.append(kmeans.inertia_)#3
    answer.append(fowlkes_mallows_score(y, labels))#4
    answer.append(jaccard_score(y, labels, average="macro"))#5
    answer.append(rand_score(y, labels))#6
    answer.append(adjusted_rand_score(y, labels))#7
    answer.append(normalized_mutual_info_score(y, labels))#8
    print("K-均值聚类已完成")
    return answer

def AC_(data,num,dis,fulltree):
    y = data.iloc[:, -1]
    y = pd.DataFrame(y)
    data = data.drop(data.columns[-1], axis=1)
    AC = AgglomerativeClustering(n_clusters=num, metric=dis, linkage='ward', compute_full_tree=fulltree)
    AC.fit(data)
    type1_ = set()
    for i in range(0, y.shape[0]):
        type1_.add(y.iloc[i, 0])
    type1 = list(type1_)
    type2 = {}
    for i in range(0, len(type1_)):
        type2[type1[i]] = i
    for i in range(0, y.shape[0]):
        y.iloc[i, 0] = type2[y.iloc[i, 0]]
    y = y.astype(int)
    data['cluster'] = AC.labels_
    data['destination'] = y
    name = data.columns.tolist()
    fig = plt.figure(figsize=(12, 8))
    plt.subplot(121)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[3]], cmap='viridis', label=f'真实的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"以{name[0]}和{name[1]}为参考特征的、以{name[2]}为目标变量的系统聚类结果:真实分类")
    plt.legend()

    # 第二个子图：预测的分类
    plt.subplot(122)
    plt.scatter(data[name[0]], data[name[1]], c=AC.labels_, cmap='viridis', label=f'预测的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"预测分类")
    plt.legend()
    plt.savefig('./static/AC.png', dpi=300, bbox_inches='tight', transparent=True)
    answer = []
    answer.append(silhouette_score(data[[name[0], name[1]]], AC.labels_))
    answer.append(calinski_harabasz_score(data[[name[0], name[1]]], AC.labels_))
    answer.append(davies_bouldin_score(data[[name[0], name[1]]], AC.labels_))
    labels = AC.labels_
    y = y.iloc[:, 0].values
    answer.append(jaccard_score(y, labels, average="macro"))
    answer.append(fowlkes_mallows_score(y, labels))
    answer.append(rand_score(y, labels))
    answer.append(adjusted_rand_score(y, labels))
    answer.append(normalized_mutual_info_score(y, labels))

    print("系统聚类已完成")
    return answer

def EM_(data,num,func,d,tol):
    y = data.iloc[:, -1]
    y = pd.DataFrame(y)
    data = data.drop(data.columns[-1], axis=1)
    EM = GaussianMixture(n_components=num,covariance_type=func,max_iter=d,tol=tol)
    EM.fit(data)
    type1_ = set()
    for i in range(0, y.shape[0]):
        type1_.add(y.iloc[i, 0])
    type1 = list(type1_)
    type2 = {}
    for i in range(0, len(type1_)):
        type2[type1[i]] = i
    for i in range(0, y.shape[0]):
        y.iloc[i, 0] = type2[y.iloc[i, 0]]
    y = y.astype(int)
    data['cluster'] = EM.predict(data)
    data['destination'] = y
    name = data.columns.tolist()
    labels = EM.predict(data[[name[0], name[1]]])
    fig = plt.figure(figsize=(12, 8))
    plt.subplot(121)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[3]], cmap='viridis', label=f'真实的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"以{name[0]}和{name[1]}为参考特征的、以{name[2]}为目标变量的基于高斯分布的EM聚类结果:真实分类")
    plt.legend()
    plt.subplot(122)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[2]], cmap='viridis', label=f'预测的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"预测分类")
    plt.legend()
    plt.savefig('./static/GMM.png', dpi=300, bbox_inches='tight', transparent=True)
    answer = []
    answer.append(silhouette_score(data[[name[0], name[1]]], labels))
    answer.append(calinski_harabasz_score(data[[name[0], name[1]]], labels))
    answer.append(davies_bouldin_score(data[[name[0], name[1]]], labels))
    y = y.iloc[:, 0].values if isinstance(y, pd.DataFrame) else y
    answer.append(jaccard_score(y, labels, average="macro"))
    answer.append(fowlkes_mallows_score(y, labels))
    answer.append(rand_score(y, labels))
    answer.append(adjusted_rand_score(y, labels))
    answer.append(normalized_mutual_info_score(y, labels))
    print("EM聚类已完成")
    return answer

#此处有源代码
def DB_(data,r,c,a):
    y = data.iloc[:, -1]
    y = pd.DataFrame(y)
    data = data.drop(data.columns[-1], axis=1)
    type1_ = set()
    for i in range(0, y.shape[0]):
        type1_.add(y.iloc[i, 0])
    type1 = list(type1_)
    type2 = {}
    for i in range(0, len(type1_)):
        type2[type1[i]] = i
    for i in range(0, y.shape[0]):
        y.iloc[i, 0] = type2[y.iloc[i, 0]]
    y = y.astype(int)
    DB=ManualDBSCAN(eps=r, min_samples=c, algorithm=a)
    DB.fit(data)
    data['cluster'] = DB.labels_
    data['destination'] = y
    name = data.columns.tolist()
    fig = plt.figure(figsize=(12, 8))
    plt.subplot(121)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[3]], cmap='viridis', label=f'真实的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"以{name[0]}和{name[1]}为参考特征的、以{name[2]}为目标变量的K聚类结果:真实分类")
    plt.legend()
    # 第二个子图：预测的分类
    plt.subplot(122)
    plt.scatter(data[name[0]], data[name[1]], c=DB.labels_, cmap='viridis', label=f'预测的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"预测分类")
    plt.legend()
    plt.savefig('./static/DB.png', dpi=300, bbox_inches='tight', transparent=True)
    answer = []
    labels = DB.labels_
    y = y.iloc[:, 0].values
    answer.append(silhouette_score(data[[name[0], name[1]]], DB.labels_))  # 0
    answer.append(calinski_harabasz_score(data[[name[0], name[1]]], DB.labels_))  # 1
    answer.append(davies_bouldin_score(data[[name[0], name[1]]], DB.labels_))  # 2
    answer.append(fowlkes_mallows_score(y, labels))  # 4
    answer.append(jaccard_score(y, labels, average="macro"))  # 5
    answer.append(rand_score(y, labels))  # 6
    answer.append(adjusted_rand_score(y, labels))  # 7
    answer.append(normalized_mutual_info_score(y, labels))  # 8
    print("DBSCAN特色聚类已完成")
    return answer

#——————————————————————————————————————————源代码结束，下面是sklearn的方法

def BYS_sk(data, destination):
    data=data.dropna()
    destination=int(destination)
    answer=[]
    modelNB=GaussianNB()
    y=data.iloc[:,destination]
    y=remath_single(y)
    x=data.drop(columns=data.columns[destination])
    x0,x1,y0,y1=train_test_split(x,y,test_size=0.75,random_state=42)
    modelNB.fit(x0,y0)
    y2=modelNB.predict(x1)
    answer.append(accuracy_score(y1,y2))#准确率
    answer.append(precision_score(y1,y2, average='weighted'))#精确率
    answer.append(recall_score(y1,y2, average='weighted'))#召回率
    answer.append(f1_score(y1,y2, average='weighted'))#F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1,y2)))#混淆矩阵
    answer.append(1-modelNB.score(x0, y0))
    answer.append(1-modelNB.score(x1, y1))

    # y_score=modelNB.predict_proba(x1)[:,1]
    # fpr,tpr,th=roc_curve(y1,y_score)
    # roc_auc=auc(fpr,tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'BYS_img.png')
    # plt.savefig(image_path)
    # plt.close()
    print("贝叶斯分类器工作完成")
    return answer
def K_neighbor_sk(data, destination, K):
    data = data.dropna()
    destination = int(destination)
    answer = []
    K=int(K)
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=42)
    modelKNN=neighbors.KNeighborsClassifier(n_neighbors=K)
    modelKNN.fit(x0,y0)
    y2=modelKNN.predict(x1)
    answer.append(accuracy_score(y1, y2))  # 准确率
    answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
    answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
    answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
    answer.append(1-modelKNN.score(x0, y0))
    answer.append(1-modelKNN.score(x1, y1))

    # y_score = modelKNN.predict_proba(x1)[:, 1]
    # fpr, tpr, th = roc_curve(y1, y_score)
    # roc_auc = auc(fpr, tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'KNN_img.png')
    # plt.savefig(image_path)
    # plt.close()

    print("KNN分类器工作完成")
    return answer

def decision_tree_sk(data, destination, deep):
    data=data.dropna()
    destination=int(destination)
    answer = []
    deep=int(deep)
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=123)

    modelDTC=tree.DecisionTreeClassifier(criterion='gini', max_depth=deep, random_state=42)
    modelDTC.fit(x0,y0)
    y2=modelDTC.predict(x1)
    answer.append(accuracy_score(y1, y2))  # 准确率
    answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
    answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
    answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
    answer.append(1-modelDTC.score(x0, y0))
    answer.append(1-modelDTC.score(x1, y1))

    # y_score = modelDTC.predict_proba(x1)[:, 1]
    # fpr, tpr, th = roc_curve(y1, y_score)
    # roc_auc = auc(fpr, tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'DTC_img.png')
    # plt.savefig(image_path)
    # plt.close()

    print("决策树分类器工作完成")
    return answer
def together_learn_sk(data, destination, type_learn, num, deep):
    data = data.dropna()
    destination = int(destination)
    answer = []
    num=int(num)
    deep = int(deep)
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=123)
    if type_learn=="RandomForestClassifier":
        clf = RandomForestClassifier(n_estimators=num, criterion='gini', max_depth=deep, random_state=42)
        clf.fit(x0,y0)
        y2=clf.predict(x1)
        answer.append(accuracy_score(y1, y2))  # 准确率
        answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
        answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
        answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
        answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
        answer.append(1-clf.score(x0, y0))
        answer.append(1-clf.score(x1, y1))

        # y_score = clf.predict_proba(x1)[:, 1]
        # fpr, tpr, th = roc_curve(y1, y_score)
        # roc_auc = auc(fpr, tpr)
        # plt.figure()
        # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
        # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        # plt.xlim([0.0, 1.0])
        # plt.ylim([0.0, 1.05])
        # plt.xlabel('False Positive Rate')
        # plt.ylabel('True Positive Rate')
        # plt.title('Receiver Operating Characteristic')
        # plt.legend(loc="lower right")
        # static_dir = os.path.join(os.path.dirname(__file__), 'static')
        # if not os.path.exists(static_dir):
        #     os.makedirs(static_dir)
        # image_path = os.path.join(static_dir, 'clf_img.png')
        # plt.savefig(image_path)
        # plt.close()

        print("集成学习分类器工作完成")
        return answer
    else:
        clf = GradientBoostingClassifier(n_estimators=num, criterion='gini', max_depth=deep, random_state=42)
        clf.fit(x0, y0)
        y2 = clf.predict(x1)
        answer.append(accuracy_score(y1, y2))  # 准确率
        answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
        answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
        answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
        answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
        answer.append(1-clf.score(x0,y0))
        answer.append(1-clf.score(x1, y1))

        # y_score = clf.predict_proba(x1)[:, 1]
        # fpr, tpr, th = roc_curve(y1, y_score)
        # roc_auc = auc(fpr, tpr)
        # plt.figure()
        # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
        # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        # plt.xlim([0.0, 1.0])
        # plt.ylim([0.0, 1.05])
        # plt.xlabel('False Positive Rate')
        # plt.ylabel('True Positive Rate')
        # plt.title('Receiver Operating Characteristic')
        # plt.legend(loc="lower right")
        # static_dir = os.path.join(os.path.dirname(__file__), 'static')
        # if not os.path.exists(static_dir):
        #     os.makedirs(static_dir)
        # image_path = os.path.join(static_dir, 'clf_img.png')
        # plt.savefig(image_path)
        # plt.close()
        print("集成学习分类器工作完成")
        return answer
import sklearn.neural_network as net
def netMLP_sk(data, destination, num, func, you):
    data = data.dropna()
    destination = int(destination)
    answer = []
    num=tuple(num)
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=123)
    NeuNet=net.MLPClassifier(hidden_layer_sizes=num,activation=func,solver=you,random_state=42)
    NeuNet.fit(x0,y0)
    y2=NeuNet.predict(x1)
    answer.append(accuracy_score(y1, y2))  # 准确率
    answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
    answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
    answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
    answer.append(1-NeuNet.score(x0, y0))
    answer.append(1-NeuNet.score(x1, y1))

    # y_score = NeuNet.predict_proba(x1)[:, 1]
    # fpr, tpr, th = roc_curve(y1, y_score)
    # roc_auc = auc(fpr, tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'net_img.png')
    # plt.savefig(image_path)
    # plt.close()

    print("人工神经网络分类器工作完成")
    return answer

def SVC__sk(data, destination, C, type, pro):
    data = data.dropna()
    destination = int(destination)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x0, x1, y0, y1 = train_test_split(x, y, test_size=0.75, random_state=42)
    svc=SVC(C=C,kernel=type,probability=pro)
    svc.fit(x0,y0)
    y2=svc.predict(x1)
    answer.append(accuracy_score(y1, y2))  # 准确率
    answer.append(precision_score(y1, y2, average='weighted'))  # 精确率
    answer.append(recall_score(y1, y2, average='weighted'))  # 召回率
    answer.append(f1_score(y1, y2, average='weighted'))  # F1分数
    answer.append(from_river_to_the_sea(confusion_matrix(y1, y2)))  # 混淆矩阵
    answer.append(1 - svc.score(x0, y0))
    answer.append(1 - svc.score(x1, y1))

    # y_score = svc.predict_proba(x1)[:, 1]
    # fpr, tpr, th = roc_curve(y1, y_score)
    # roc_auc = auc(fpr, tpr)
    # plt.figure()
    # plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    # plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    # plt.xlabel('False Positive Rate')
    # plt.ylabel('True Positive Rate')
    # plt.title('Receiver Operating Characteristic')
    # plt.legend(loc="lower right")
    # static_dir = os.path.join(os.path.dirname(__file__), 'static')
    # if not os.path.exists(static_dir):
    #     os.makedirs(static_dir)
    # image_path = os.path.join(static_dir, 'svc_img.png')
    # plt.savefig(image_path)
    # plt.close()

    print("支持向量机分类器工作完成")
    return answer

def VT_sk(data, goal, threshold, dataq):
    data = data.dropna()
    destination = int(goal)
    threshold=float(threshold)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    xx=dataq.drop(columns=dataq.columns[destination])
    selector=VarianceThreshold(threshold=threshold)
    X=selector.fit_transform(x)
    X=pd.DataFrame(X)
    y=pd.DataFrame(y)
    answer.append(X)
    answer.append(y)
    answer.append(x.columns.tolist())
    answer.append(x.var().to_dict())
    answer.append(selector.get_support())
    answer.append(X.shape[1])
    print("过滤式策略下的低方差选择特征完成")
    return answer
def SK_sk(data, goal, func, threshold, dataq):
    data = data.dropna()
    destination = int(goal)
    threshold = int(threshold)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    xx = dataq.drop(columns=dataq.columns[destination])
    selector = SelectKBest(score_func=f_classif, k=threshold)
    if func=='f_classif':
        pass
    elif func=='chi2':
        selector = SelectKBest(score_func=chi2, k=threshold)
    elif func=='mutual_info_classif':
        selector = SelectKBest(score_func=mutual_info_classif, k=threshold)
    elif func=='f_regression':
        selector = SelectKBest(score_func=f_regression, k=threshold)
    elif func=='mutual_info_regression':
        selector = SelectKBest(score_func=mutual_info_regression, k=threshold)
    X = selector.fit_transform(x,y)
    X = pd.DataFrame(X)
    y = pd.DataFrame(y)
    # 查看选择的特征
    # print("\n选择后的特征：")
    # print(X[:5])  # 打印前5行
    # # 查看每个特征的评分
    # print("\n特征评分：")
    # print(selector.scores_)
    # # # 查看哪些特征被选中
    # # print("\n被选中的特征：")
    # # print(selector.support_)
    # # # 查看特征排名
    # # print("\n特征排名：")
    # # print(selector.ranking_)
    # # 查看每个特征的p值
    # print("\n特征的p值：")
    # print(selector.pvalues_)
    answer.append(X)
    answer.append(y)
    answer.append(selector.scores_)
    answer.append(selector.pvalues_)
    answer.append(selector.get_support())#布尔掩码
    print("过滤式策略下的高相关选择特征完成")
    return answer

def RFE__sk(data, goal, num, obj, step):
    data = data.dropna()
    destination = int(goal)
    num=int(num)
    step=int(step)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    y=pd.DataFrame(y)
    y=y.astype(int)
    # print(y)
    # print(np.unique(y))
    # print(y.dtypes)
    x = data.drop(columns=data.columns[destination])
    estimator = SVC(kernel="linear")
    if obj=="SVM":
        pass
    elif obj=="Logistic Regression":
        estimator = LogisticRegression(max_iter=1000)
    elif obj=="Linear Regression":
        estimator = LinearRegression()
    elif obj=="Ridge Regression":
        estimator = Ridge(alpha=1.0)
    elif obj=="Decision Tree":
        estimator = DecisionTreeClassifier()
    elif obj=="Lasso":
        estimator = Lasso(alpha=0.1)
    elif obj=="Gradient Boosting":
        estimator = GradientBoostingClassifier(n_estimators=100)
    elif obj=="Random Forest":
        estimator = RandomForestClassifier(n_estimators=100)
    elif obj=="LDA":
        estimator = LinearDiscriminantAnalysis()
    selector=RFE(estimator=estimator,n_features_to_select=num,step=step)
    selector.fit(x,y)
    # print("保留的特征：", selector.support_)
    # print("特征排名：", selector.ranking_)
    X=selector.transform(x)
    X=pd.DataFrame(X)
    y=pd.DataFrame(y)
    answer.append(X)
    answer.append(y)
    answer.append(selector.support_)
    answer.append(selector.ranking_)
    print("包裹式特征选择策略完成")
    return answer

def Lasso__sk(data, goal, num, round, tol, ni, dataq):
    data = data.dropna()
    destination = int(goal)
    num = float(num)
    round=int(round)
    tol=float(tol)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)

    x = data.drop(columns=data.columns[destination])
    x = pd.DataFrame(x)
    y = pd.DataFrame(y)
    y = y.astype(int)
    dataqq = dataq.drop(columns=dataq.columns[goal])
    x.columns=dataqq.columns.tolist()
    y.columns = [dataq.columns.tolist()[goal]]
    lasso=Lasso(alpha=num,max_iter=round,tol=tol,fit_intercept=ni,random_state=42)
    lasso.fit(x,y)
    # print("特征系数:", {k: float(v) for k, v in dict(zip(x.columns, lasso.coef_)).items()})
    # print("截距项：", lasso.intercept_)
    # print("被淘汰的特征:", x.columns[lasso.coef_ == 0])
    key=[]
    for k,v in dict(zip(x.columns, lasso.coef_)).items():
        if v<=0:
            continue
        else:
            key.append(k)
    off=x.columns[lasso.coef_ == 0]
    character={k:float(v) for k,v in dict(zip(x.columns, lasso.coef_)).items()}
    x=x[key]
    answer.append(x)
    answer.append(y)
    answer.append(character)
    answer.append(lasso.intercept_)
    answer.append(off)
    answer.append(key)
    print("基于Lasso回归的嵌入式特征选择策略完成")
    return answer
def ridge_sk(data, goal, num, round, tol, ni, gui, dataq, limit):
    data = data.dropna()
    destination = int(goal)
    print("\n"*100)
    print(data)
    print("*"*100)
    print(dataq)
    num = float(num)
    round = int(round)
    tol = float(tol)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    print(y)
    print(np.unique(y))
    x = data.drop(columns=data.columns[destination])
    scaler = StandardScaler()
    if gui:
        x=scaler.fit_transform(x)
    x = pd.DataFrame(x)
    y = pd.DataFrame(y)
    y = y.astype(int)
    dataqq = dataq.drop(columns=dataq.columns[goal])
    x.columns = dataqq.columns.tolist()
    y.columns = [dataq.columns.tolist()[goal]]
    ridge=Ridge(alpha=num,max_iter=round,tol=tol,fit_intercept=ni,random_state=42)
    ridge.fit(x,y)
    # print("特征系数：", ridge.coef_)
    # print("截距项：", ridge.intercept_)
    absf=abs(ridge.coef_)
    un=np.where(absf<limit)[0]
    final=[]
    not_final=[]
    for i in range(0,len(absf)):
        # print("当前是",dataq.columns.tolist()[i],"un[i]:",absf[i],";","limit:",limit)
        if absf[i]<limit:
            not_final.append(dataq.columns.tolist()[i])
        else:
            final.append(i)
    x=x.iloc[:,final]
    # print(x)
    # print(not_final)
    answer.append(x)
    answer.append(y)
    answer.append(ridge.coef_)
    answer.append(ridge.intercept_)
    answer.append(not_final)
    print("基于岭回归的嵌入式特征选择策略完成")
    return answer

def elastic_sk(data, goal, num, round, L1, tol, ni, gui, dataq, limit):
    data = data.dropna()
    destination = int(goal)
    num = float(num)
    round = int(round)
    tol = float(tol)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    scaler = StandardScaler()
    if gui:
        x = scaler.fit_transform(x)
    x = pd.DataFrame(x)
    y = pd.DataFrame(y)
    y = y.astype(int)
    dataqq = dataq.drop(columns=dataq.columns[goal])
    x.columns = dataqq.columns.tolist()
    y.columns = [dataq.columns.tolist()[goal]]
    elastic_net=ElasticNet(alpha=num,max_iter=round,l1_ratio=L1,tol=tol,fit_intercept=ni,random_state=42)
    elastic_net.fit(x,y)
    key=[]
    final=[]
    not_final=[]
    actual={}
    for i in range(0,len(dataqq.columns.tolist())):
        actual[dataqq.columns.tolist()[i]]=elastic_net.coef_[i]
        if abs(elastic_net.coef_[i])<limit:
            not_final.append(dataqq.columns.tolist()[i])
        else:
            key.append(i)
            final.append(dataqq.columns.tolist()[i])
    x=x.iloc[:,key]
    print("特征系数：", elastic_net.coef_)
    print("截距项：", elastic_net.intercept_)
    print("实际迭代次数：", elastic_net.n_iter_)
    answer.append(x)
    answer.append(y)
    answer.append(final)#被选中的
    answer.append(not_final)#被筛选的
    answer.append(actual)#各个特征的特征系数
    answer.append(elastic_net.intercept_)#截距项
    answer.append(elastic_net.n_iter_)#迭代次数
    print("基于弹性网的嵌入式特征选择策略完成")
    return answer

def PCA__sk(data, aim, num, white, solve, dataq):
    data = data.dropna()
    destination = int(aim)
    num = int(num)
    answer = []
    y = data.iloc[:, destination]
    y = remath_single(y)
    x = data.drop(columns=data.columns[destination])
    x = pd.DataFrame(x)

    y = pd.DataFrame(y)
    dataqq = dataq.drop(columns=dataq.columns[destination])
    x.columns = dataqq.columns.tolist()
    y.columns = [dataq.columns.tolist()[destination]]
    print(x)
    pca=PCA(n_components=num,whiten=white,svd_solver=solve,random_state=42)
    pca.fit(x)
    # print("2主成分的权重向量:", pca.components_)
    # print("3每个主成分所解释的方差大小", pca.explained_variance_)
    # print("4每个主成分所解释的方差占总方差的比例:", pca.explained_variance_ratio_)
    # print("5奇异值:", pca.singular_values_)
    # print("6数据的均值:", pca.mean_)
    # print("7实际保留的主成分数量:", pca.n_components_)
    # print("8噪声的方差:", pca.noise_variance_)
    X=pca.fit_transform(x)
    X=pd.DataFrame(X)

    answer.append(X)
    answer.append(y)
    answer.append(pca.components_)
    answer.append(pca.explained_variance_)
    answer.append(pca.explained_variance_ratio_)
    answer.append(pca.singular_values_)
    answer.append(pca.mean_)
    answer.append(pca.n_components_)
    answer.append(pca.noise_variance_)


    # plt.figure(figsize=(8, 6))
    # plt.scatter(X[:, 0], X[:, 1], alpha=0.5, label='原始数据点')
    # plt.scatter(X_pca, np.zeros_like(X_pca), c='red', alpha=0.5, label='筛选后的主成分数据')
    # plt.xlabel('Feature 1')
    # plt.ylabel('Feature 2')
    # plt.title('PCA 数据降维可视化')
    # plt.legend()
    # plt.grid(True)


    print("主成分分析完成")
    return answer

def KN_cluster_sk(data, first, second, num, func, seed, d, tol):
    y=data.iloc[:,-1]
    y=pd.DataFrame(y)
    data = data.drop(data.columns[-1], axis=1)
    kmeans = KMeans(n_clusters=num, init=func, n_init=seed, max_iter=d, tol=tol, random_state=42)
    kmeans.fit(data)
    type1_=set()
    for i in range(0,y.shape[0]):
        type1_.add(y.iloc[i,0])
    type1=list(type1_)
    type2={}
    for i in range(0,len(type1_)):
        type2[type1[i]]=i
    for i in range(0,y.shape[0]):
        y.iloc[i,0]=type2[y.iloc[i,0]]
    y=y.astype(int)
    data['cluster']=kmeans.labels_
    data['destination']=y
    name=data.columns.tolist()
    fig = plt.figure(figsize=(12, 8))
    plt.subplot(121)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[3]], cmap='viridis', label=f'真实的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"以{name[0]}和{name[1]}为参考特征的、以{name[2]}为目标变量的K聚类结果:真实分类")
    plt.legend()

    # 第二个子图：预测的分类
    plt.subplot(122)
    plt.scatter(data[name[0]], data[name[1]], c=kmeans.labels_, cmap='viridis', label=f'预测的{name[2]}分类')
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=100, c='red', marker='X',
                label='聚类中心')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"预测分类")
    plt.legend()
    plt.savefig('./static/KN.png', dpi=300, bbox_inches='tight', transparent=True)
    answer=[]
    labels=kmeans.labels_
    y = y.iloc[:, 0].values
    answer.append(silhouette_score(data[[name[0], name[1]]], kmeans.labels_))#0
    answer.append(calinski_harabasz_score(data[[name[0], name[1]]], kmeans.labels_))#1
    answer.append(davies_bouldin_score(data[[name[0], name[1]]], kmeans.labels_))#2
    answer.append(kmeans.inertia_)#3
    answer.append(fowlkes_mallows_score(y, labels))#4
    answer.append(jaccard_score(y, labels, average="macro"))#5
    answer.append(rand_score(y, labels))#6
    answer.append(adjusted_rand_score(y, labels))#7
    answer.append(normalized_mutual_info_score(y, labels))#8
    print("K-均值聚类已完成")
    return answer
def AC__sk(data, num, dis, fulltree):
    y = data.iloc[:, -1]
    y = pd.DataFrame(y)
    data = data.drop(data.columns[-1], axis=1)
    AC = AgglomerativeClustering(n_clusters=num, metric=dis, linkage='ward', compute_full_tree=fulltree)
    AC.fit(data)
    type1_ = set()
    for i in range(0, y.shape[0]):
        type1_.add(y.iloc[i, 0])
    type1 = list(type1_)
    type2 = {}
    for i in range(0, len(type1_)):
        type2[type1[i]] = i
    for i in range(0, y.shape[0]):
        y.iloc[i, 0] = type2[y.iloc[i, 0]]
    y = y.astype(int)
    data['cluster'] = AC.labels_
    data['destination'] = y
    name = data.columns.tolist()
    fig = plt.figure(figsize=(12, 8))
    plt.subplot(121)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[3]], cmap='viridis', label=f'真实的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"以{name[0]}和{name[1]}为参考特征的、以{name[2]}为目标变量的系统聚类结果:真实分类")
    plt.legend()

    # 第二个子图：预测的分类
    plt.subplot(122)
    plt.scatter(data[name[0]], data[name[1]], c=AC.labels_, cmap='viridis', label=f'预测的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"预测分类")
    plt.legend()
    plt.savefig('./static/AC.png', dpi=300, bbox_inches='tight', transparent=True)
    answer = []
    answer.append(silhouette_score(data[[name[0], name[1]]], AC.labels_))
    answer.append(calinski_harabasz_score(data[[name[0], name[1]]], AC.labels_))
    answer.append(davies_bouldin_score(data[[name[0], name[1]]], AC.labels_))
    labels = AC.labels_
    y = y.iloc[:, 0].values
    answer.append(jaccard_score(y, labels, average="macro"))
    answer.append(fowlkes_mallows_score(y, labels))
    answer.append(rand_score(y, labels))
    answer.append(adjusted_rand_score(y, labels))
    answer.append(normalized_mutual_info_score(y, labels))

    print("系统聚类已完成")
    return answer

def EM__sk(data, num, func, d, tol):
    y = data.iloc[:, -1]
    y = pd.DataFrame(y)
    data = data.drop(data.columns[-1], axis=1)
    EM = GaussianMixture(n_components=num,covariance_type=func,max_iter=d,tol=tol)
    EM.fit(data)
    type1_ = set()
    for i in range(0, y.shape[0]):
        type1_.add(y.iloc[i, 0])
    type1 = list(type1_)
    type2 = {}
    for i in range(0, len(type1_)):
        type2[type1[i]] = i
    for i in range(0, y.shape[0]):
        y.iloc[i, 0] = type2[y.iloc[i, 0]]
    y = y.astype(int)
    data['cluster'] = EM.predict(data)
    data['destination'] = y
    name = data.columns.tolist()
    labels = EM.predict(data[[name[0], name[1]]])
    fig = plt.figure(figsize=(12, 8))
    plt.subplot(121)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[3]], cmap='viridis', label=f'真实的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"以{name[0]}和{name[1]}为参考特征的、以{name[2]}为目标变量的基于高斯分布的EM聚类结果:真实分类")
    plt.legend()
    plt.subplot(122)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[2]], cmap='viridis', label=f'预测的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"预测分类")
    plt.legend()
    plt.savefig('./static/GMM.png', dpi=300, bbox_inches='tight', transparent=True)
    answer = []
    answer.append(silhouette_score(data[[name[0], name[1]]], labels))
    answer.append(calinski_harabasz_score(data[[name[0], name[1]]], labels))
    answer.append(davies_bouldin_score(data[[name[0], name[1]]], labels))
    y = y.iloc[:, 0].values if isinstance(y, pd.DataFrame) else y
    answer.append(jaccard_score(y, labels, average="macro"))
    answer.append(fowlkes_mallows_score(y, labels))
    answer.append(rand_score(y, labels))
    answer.append(adjusted_rand_score(y, labels))
    answer.append(normalized_mutual_info_score(y, labels))
    print("EM聚类已完成")
    return answer

def DB__sk(data, r, c, a):
    y = data.iloc[:, -1]
    y = pd.DataFrame(y)
    data = data.drop(data.columns[-1], axis=1)
    type1_ = set()
    for i in range(0, y.shape[0]):
        type1_.add(y.iloc[i, 0])
    type1 = list(type1_)
    type2 = {}
    for i in range(0, len(type1_)):
        type2[type1[i]] = i
    for i in range(0, y.shape[0]):
        y.iloc[i, 0] = type2[y.iloc[i, 0]]
    y = y.astype(int)
    DB=DBSCAN(eps=r,min_samples=c,algorithm=a)
    DB.fit(data)
    data['cluster'] = DB.labels_
    data['destination'] = y
    name = data.columns.tolist()
    fig = plt.figure(figsize=(12, 8))
    plt.subplot(121)
    plt.scatter(data[name[0]], data[name[1]], c=data[name[3]], cmap='viridis', label=f'真实的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"以{name[0]}和{name[1]}为参考特征的、以{name[2]}为目标变量的K聚类结果:真实分类")
    plt.legend()
    # 第二个子图：预测的分类
    plt.subplot(122)
    plt.scatter(data[name[0]], data[name[1]], c=DB.labels_, cmap='viridis', label=f'预测的{name[2]}分类')
    plt.xlabel(name[0])
    plt.ylabel(name[1])
    plt.title(f"预测分类")
    plt.legend()
    plt.savefig('./static/DB.png', dpi=300, bbox_inches='tight', transparent=True)
    answer = []
    labels = DB.labels_
    y = y.iloc[:, 0].values
    unique_labels = np.unique(labels)
    answer.append(silhouette_score(data[[name[0], name[1]]], DB.labels_))  # 0
    answer.append(calinski_harabasz_score(data[[name[0], name[1]]], DB.labels_))  # 1
    answer.append(davies_bouldin_score(data[[name[0], name[1]]], DB.labels_))  # 2
    answer.append(fowlkes_mallows_score(y, labels))  # 4
    answer.append(jaccard_score(y, labels, average="macro"))  # 5
    answer.append(rand_score(y, labels))  # 6
    answer.append(adjusted_rand_score(y, labels))  # 7
    answer.append(normalized_mutual_info_score(y, labels))  # 8
    print("DBSCAN特色聚类已完成")
    return answer

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOW

@app.route('/')
def go_home():
    return render_template('home.html')
@app.route('/home', methods=['GET', 'POST'])
def make_file():
    """处理文件上传"""
    if request.method == 'POST':
        # 检查是否有文件在请求中
        if 'file' not in request.files:
            flash('没有文件部分')
            return redirect(request.url)

        file = request.files['file']

        # 如果用户没有选择文件，浏览器也会提交一个空的文件部分
        if file.filename == '':
            flash('没有选择文件')
            return redirect(request.url)

        # 检查文件类型是否允许
        if file and allowed_file(file.filename):
            # 保存文件到指定路径
            filename = file.filename
            file_path = os.path.join('static', filename)
            file.save(file_path)  # 保存文件
            flash('文件上传成功')
            flash('正在分析')
            # if filename.rsplit('.', 1)[1].lower() =='csv':
            #     first_learning(file_path,1)
            # elif filename.rsplit('.', 1)[1].lower() =='xlsx':
            #     first_learning(file_path, 2)
            # elif filename.rsplit('.', 1)[1].lower() =='xls':
            #     first_learning(file_path, 3)
            try:
                if filename.endswith('.csv'):
                    data = pd.read_csv(file_path)
                elif filename.endswith('.xlsx'):
                    data = pd.read_excel(file_path)
                else:
                    flash('不支持的文件类型')
                    return redirect(request.url)
                data1 = pre_doing(data)
                f.append(data1)
                f.append(data)
                data=data.head()
                print(data)

                # 将数据转换为 HTML 表格
                data2=data1.head()
                print(data1)
                data_html = data.to_html(index=False, classes='table table-striped')
                data2_html=data2.to_html(index=False,classes='table table-striped')
                return render_template('display.html', data=data_html,data1=data2_html)
            except Exception as e:
                flash(f"读取文件失败：{e}")
                return redirect(request.url)
        else:
            flash('不允许的文件类型')
            return redirect(request.url)
    return render_template('error2.html')
data_name={"vt":"基于过滤式策略下的低方差过滤数据",'sk':"基于过滤式策略下的高相关过滤数据"}

@app.route('/home_sklearn', methods=['GET', 'POST'])
def make_file_sklearn():
    """处理文件上传"""
    if request.method == 'POST':
        # 检查是否有文件在请求中
        if 'file' not in request.files:
            flash('没有文件部分')
            return redirect(request.url)

        file = request.files['file']

        # 如果用户没有选择文件，浏览器也会提交一个空的文件部分
        if file.filename == '':
            flash('没有选择文件')
            return redirect(request.url)

        # 检查文件类型是否允许
        if file and allowed_file(file.filename):
            # 保存文件到指定路径
            filename = file.filename
            file_path = os.path.join('static', filename)
            file.save(file_path)  # 保存文件
            flash('文件上传成功')
            flash('正在分析')
            # if filename.rsplit('.', 1)[1].lower() =='csv':
            #     first_learning(file_path,1)
            # elif filename.rsplit('.', 1)[1].lower() =='xlsx':
            #     first_learning(file_path, 2)
            # elif filename.rsplit('.', 1)[1].lower() =='xls':
            #     first_learning(file_path, 3)
            try:
                if filename.endswith('.csv'):
                    data = pd.read_csv(file_path)
                elif filename.endswith('.xlsx'):
                    data = pd.read_excel(file_path)
                else:
                    flash('不支持的文件类型')
                    return redirect(request.url)
                data1 = pre_doing(data)
                f.append(data1)
                f.append(data)
                data=data.head()
                print(data)

                # 将数据转换为 HTML 表格
                data2=data1.head()
                print(data1)
                data_html = data.to_html(index=False, classes='table table-striped')
                data2_html=data2.to_html(index=False,classes='table table-striped')
                return render_template('display_sklearn.html', data=data_html,data1=data2_html)
            except Exception as e:
                flash(f"读取文件失败：{e}")
                return redirect(request.url)
        else:
            flash('不允许的文件类型')
            return redirect(request.url)
    return render_template('error2.html')


#————————————————下面开始是对源代码方法进行操作————————————
@app.route('/display',methods=['GET','POST'])
def display():
    data=f[0]
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    data = pd.DataFrame(data)
    destination=int(request.form.get('destination'))
    k=request.form.get("K")
    decision_deep=request.form.get("decision_deep")
    if decision_deep=='':
        de_tree_obj_list=decision_tree(data,destination,3)
        decision_deep=3
    else:
        de_tree_obj_list = decision_tree(data, destination, decision_deep)
    if k=='' or int(k)<=0:
        Knn_obj_list=K_neighbor(data,destination,5)
        k=5
    else:
        Knn_obj_list=K_neighbor(data,destination,int(k))
    bys_obj_list=BYS(data,destination)
    type_of_forest="RandomForestClassifier" if request.form.get("option") is None else request.form.get("option")
    learn_num=100 if request.form.get("learn_num")=="" else request.form.get("learn_num")
    tree_num = 3 if request.form.get("tree_num") == "" else request.form.get("tree_num")
    togeter_obj_list=together_learn(data,destination,type_of_forest,learn_num,tree_num)
    type_of_forest_name="随机森林" if type_of_forest=="RandomForestClassifier" else "梯度提升"
    MLPstruct="100 50" if request.form.get("MLP_num") == '' else request.form.get("MLP_num")
    MLP_num=MLPstruct.split(" ")
    MLP_num=[int(k) for k in MLP_num]
    MLP_func=request.form.get("opt")
    MLP_you=request.form.get("solver")
    net_obj_list=netMLP(data,destination,MLP_num,MLP_func,MLP_you)
    MLP_dict={"indentity":"线性激活","logistic":"逻辑激活函数","tanh":'双曲正切激活函数',"relu":"修正线性单元"}
    solve_dict={"lbfgs":"LBFGS","sgd":"随机梯度下降","adam":"自适应矩估计"}
    func_name=MLP_dict[MLP_func]
    you_name=solve_dict[MLP_you]

    svc_num=1.0 if request.form.get("SVC_num")=='' else request.form.get("SVC_num")
    svc_func=request.form.get("SVC_type")
    svc_pro= True if request.form.get("SVC_pro") =="on" else False
    svc_func_name={"linear":"线性核","poly":"多项式核","rbf":"高斯核","sigmoid":"Sigmoid核","precomputed":"预计算核"}
    svc_pro_name="" if svc_pro else "不"


    return render_template('answer.html',dataname="",BYS=bys_obj_list,KNN=Knn_obj_list,k=k,detree=de_tree_obj_list,dedeep=decision_deep,
                           one=togeter_obj_list,together_name=type_of_forest_name,learn_num=learn_num,tree_num=tree_num,
                           Net=net_obj_list,Net_num=len(MLP_num),func_name=func_name,you_name=you_name,
                           svc=SVC_(data,destination,svc_num,svc_func,svc_pro),svc_func_name=svc_func_name[svc_func],svc_pro_name=svc_pro_name,C=svc_num)



@app.route('/display2',methods=['GET','POST'])
def display2():
    data = f[0]
    dataq=f[1]
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    data = pd.DataFrame(data)
    goal=int(request.form.get('goal'))
    VTnum=0.2 if request.form.get("VT")=='' else request.form.get("VT")
    VT_list=VT(data,goal,VTnum,dataq)
    saving_list = []
    dataqq = dataq.drop(columns=dataq.columns[goal])
    for i in range(0, len(VT_list[4])):
        if VT_list[4][i] == True:
            saving_list.append(dataqq.columns.tolist()[i])
    VT_list[0].columns = saving_list
    VT_list[1].columns = [dataq.columns.tolist()[goal]]
    vtx=VT_list[0].head()
    vtx=vtx.to_html(index=False, classes='table table-striped')
    vty = VT_list[1].head()
    vty=vty.to_html(index=False, classes='table table-striped')
    # vtx=VT_list[0][:,6].to_html(index=False, classes='table table-striped')
    # vty = VT_list[1][:,6].to_html(index=False, classes='table table-striped')
    name_list=dataq.columns.tolist()
    name_dict={}
    for i in data.columns.tolist():
        name_dict[data.columns.tolist()[i]]=name_list[i]
    new_dict={}
    for k,v in VT_list[3].items():
        new_name=name_list[k]
        new_dict[new_name]=v
    VT_list[3]=new_dict
    vtdata=pd.concat([VT_list[0],VT_list[1]],axis=1)
    all_data["vt"]=vtdata


    SKnum=int(np.floor(data.shape[1]/2)) if request.form.get("SK")=='' else request.form.get("SK")
    SKfunc=request.form.get("function")
    SK_list=SK(data,goal,SKfunc,SKnum,dataq)
    sk_saving=[]
    for i in range(0,len(dataqq.columns.tolist())):
        if SK_list[4][i]==True:
            sk_saving.append(dataq.columns.tolist()[i])
    SK_list[0].columns = sk_saving
    SK_list[1].columns = [dataq.columns.tolist()[goal]]
    skx=SK_list[0].head()
    sky=SK_list[1].head()
    skx=skx.to_html(index=False, classes='table table-striped')
    sky=sky.to_html(index=False, classes='table table-striped')
    sk_dict={}
    sk_p={}
    for i in range(0,len(saving_list)):
        sk_dict[saving_list[i]]=SK_list[2][i]
        sk_p[saving_list[i]]=SK_list[3][i]
    SK_list[2]=sk_dict
    SK_list[3]=sk_p
    skdata = pd.concat([SK_list[0], SK_list[1]], axis=1)
    all_data['sk']=skdata




    RFE_num=int(np.floor(data.shape[1]/2)) if request.form.get("now_feature")=='' else request.form.get("now_feature")
    rfe_obj=request.form.get("base_obj")
    step=1 if (request.form.get("step")=="" or request.form.get("step")>data.shapes[1]) else request.form.get("step")
    RFE_list=RFE_(data,goal,RFE_num,rfe_obj,step)
    RFE_list[1].columns = [dataq.columns.tolist()[goal]]
    rfe_name=[]
    for i in range(0, len(dataqq.columns.tolist())):
        if RFE_list[2][i]:
            rfe_name.append(dataq.columns.tolist()[i])
    RFE_list[0].columns=rfe_name

    rank={}
    for i in range(0,len(RFE_list[3])):
        rank[i] = dataq.columns.tolist()[i] + "在第" + str(RFE_list[3][i]) + "次迭代筛选时被选中"
    ca=""
    for i in range(0, len(RFE_list[3])):
        ca+="特征"+str(rank[i])+"<br>"

    # now_name = [rfe_name[i] for i, value in enumerate(RFE_list[2]) if value]
    rfex=RFE_list[0].head().to_html(index=False, classes='table table-striped')
    rfey=RFE_list[1].head().to_html(index=False, classes='table table-striped')
    rfedata=pd.concat([RFE_list[0],RFE_list[1]],axis=1)
    all_data['rfe']=rfedata
    data_name['rfe']="基于包裹式策略下的特征选择过滤数据的"


    Lanum=1.0 if request.form.get("Lassonum")=='' else request.form.get("Lassonum")==''
    Lamost=1000 if request.form.get("Lassoround")=='' else request.form.get("Lassoround")
    Latol=0.0001 if request.form.get("tol")== '' else request.form.get("tol")
    Lani=True if request.form.get("ni")=="on" else False
    LA=Lasso_(data,goal,Lanum,Lamost,Latol,Lani,dataq)
    LAx=LA[0].head().to_html(index=False, classes='table table-striped')
    LAy=LA[1].head().to_html(index=False, classes='table table-striped')
    LA[4]=LA[4].tolist()
    LAdata=pd.concat([LA[0],LA[1]],axis=1)
    all_data['lasso']=LAdata
    data_name['lasso']="基于嵌入式策略下的Lasso回归过滤数据"

    lnum=1.0 if request.form.get('lnum')=='' else request.form.get('lnum')
    lround=1000 if request.form.get("lround")=='' else request.form.get("lround")
    ltol=0.0001 if request.form.get("ltol")=='' else request.form.get("ltol")
    lni = True if request.form.get("lni") == "on" else True
    lgui=False if request.form.get("lni")=="off" else True
    limit=1 if request.form.get("llimit")=='' else request.form.get('llimit')
    LIN=ridge(data,goal,lnum,lround,ltol,lni,lgui,dataq,limit)
    LINx=LIN[0].head().to_html(index=False, classes='table table-striped')
    LINy=LIN[1].head().to_html(index=False, classes='table table-striped')
    LINnum={}
    for i in range(0,len(LIN[2])):
        LINnum[dataqq.columns.tolist()[i]]=LIN[2][i]
    LINdata=pd.concat([LIN[0],LIN[1]],axis=1)
    all_data['lin']=LINdata
    data_name['lin']="基于嵌入式策略下的岭回归特征选择过滤数据"

    softnum = 1.0 if request.form.get('softnum') == '' else float(request.form.get('softnum'))
    softround = 1000 if request.form.get("softround") == '' else int(request.form.get("softround"))
    softtol = 0.0001 if request.form.get("softtol") == '' else float(request.form.get("softtol"))
    softni = True if request.form.get("softni") == "on" else True
    softgui = False if request.form.get("softni") == "off" else True
    softimit = 0.3 if request.form.get("softlimit") == '' else float(request.form.get('softlimit'))
    softL=0.5 if request.form.get("softL1")=='' else request.form.get("softL1")
    softL=float(softL)
    if softL<=0:
        softL=0
    elif softL>=1:
        softL=1
    ELS=elastic(data,goal,softnum,softround,softL,softtol,softni,softgui,dataq,softimit)
    ELSx=ELS[0].head().to_html(index=False, classes='table table-striped')
    ELSy=ELS[1].head().to_html(index=False, classes='table table-striped')
    ELSdata=pd.concat([ELS[0],ELS[1]],axis=1)
    all_data['els']=ELSdata
    data_name['els']='基于嵌入式策略下的弹性网特征选择过滤数据'




    return render_template("answer2.html",VT=VT_list,vtx=vtx,vty=vty,vt_head_name=dataq.columns.tolist(),
                           SK=SK_list,skx=skx,sky=sky,
                           RFE=RFE_list,rfe_name=rfe_name,rfex=rfex,rfey=rfey,ca=ca,
                           LA=LA,LAx=LAx,LAy=LAy,
                           LIN=LIN,LINx=LINx,LINy=LINy,LINnum=LINnum,
                           ELS=ELS,ELSx=ELSx,ELSy=ELSy)
@app.route('/display3',methods=['GET','POST'])
def display3():
    data = f[0]
    dataq = f[1]
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    data = pd.DataFrame(data)
    aim=int(request.form.get("aim"))
    num=int(data.shape[1]/2) if request.form.get("num")=='' else request.form.get("num")
    white=True if request.form.get("white")=='on' else False
    solve=request.form.get("solve")
    pcalist=PCA_(data,aim,num,white,solve,dataq)
    dataqq = dataq.drop(columns=dataq.columns[aim])
    pcax=pcalist[0].head().to_html(index=False, classes='table table-striped')
    pcay=pcalist[1].head().to_html(index=False, classes='table table-striped')
    pcadata=pd.DataFrame(pcalist[2],columns=dataqq.columns.tolist())
    pcadata=pcadata.to_html(index=False, classes='table table-striped')
    pcalist[6] = np.reshape(pcalist[6], (1, len(pcalist[6])))
    pcalist[6]=pd.DataFrame(pcalist[6],columns=dataqq.columns.tolist())
    pcalist[6]=pcalist[6].to_html(index=False, classes='table table-striped')
    return render_template("answer3.html",pca=pcalist,pcax=pcax,pcay=pcay,pcadata=pcadata)

@app.route('/display4',methods=['GET','POST'])
def display4():
    data = f[0]
    dataq = f[1]
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    first = int(request.form.get("first"))
    second = int(request.form.get("second"))
    aim=int(request.form.get("aim"))
    data=data.iloc[:,[first,second,aim]]
    data = pd.DataFrame(data)
    dataqq = dataq.iloc[:,[first,second,aim]]
    data.columns = dataqq.columns
    KCnum=4 if request.form.get('KCnum')=='' else int(request.form.get('KCnum'))
    Kfunc=request.form.get('Kfunc')
    KNseed=10 if request.form.get('KNseed')=='' else int(request.form.get('KNseed'))
    KNd=300 if request.form.get("KNd")=='' else int(request.form.get("KNd"))
    KNtol=0.0001 if request.form.get("KNtol")=='' else float(request.form.get("KNtol"))
    KN=KN_cluster(data,first,second,KCnum,Kfunc,KNseed,KNd,KNtol)


    ACnum=4 if request.form.get("ACnum")=='' else int(request.form.get("ACnum"))
    ACdis=request.form.get("ACdistance")
    fulltree='auto' if request.form.get("fulltree")=='auto' else True if request.form.get("fulltree")=='on' else False
    AC=AC_(data,ACnum,ACdis,fulltree)

    EMnum=4 if request.form.get("EMnum")=='' else int(request.form.get("EMnum"))
    EMfunc=request.form.get("type_of_EM")
    EMd=100 if request.form.get("EMd")=='' else int(request.form.get("EMd"))
    EMtol=0.001 if request.form.get("EMtol")=='' else float(request.form.get("EMtol"))
    EM=EM_(data,EMnum,EMfunc,EMd,EMtol)

    DBr=0.05 if request.form.get("DBr")=='' else float(request.form.get("DBr"))
    DBcenter=15 if request.form.get("DBcenter")=='' else int(request.form.get("DBcenter"))
    alg=request.form.get("DBalg")

    DB=DB_(data,DBr,DBcenter,alg)
    return render_template('answer4.html',kn=KN,knnum=KCnum,Kfunc=Kfunc,KNseed=KNseed,KNd=KNd,KNtol=KNtol,
                           ac=AC,em=EM,DB=DB)


@app.route('/datago',methods=['GET','POST'])
def datago():
    data=all_data[request.form.get("type_of_data")]
    dataname=data_name[request.form.get("type_of_data")]
    dataname+="的"
    destination=-1
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    k=request.form.get("K")
    decision_deep=request.form.get("decision_deep")
    if decision_deep=='':
        de_tree_obj_list=decision_tree(data,destination,3)
        decision_deep=3
    else:
        de_tree_obj_list = decision_tree(data, destination, decision_deep)
    if k=='' or int(k)<=0:
        Knn_obj_list=K_neighbor(data,destination,5)
        k=5
    else:
        Knn_obj_list=K_neighbor(data,destination,int(k))
    bys_obj_list=BYS(data,destination)
    type_of_forest="RandomForestClassifier" if request.form.get("option") is None else request.form.get("option")
    learn_num=100 if request.form.get("learn_num")=="" else request.form.get("learn_num")
    tree_num = 3 if request.form.get("tree_num") == "" else request.form.get("tree_num")
    togeter_obj_list=together_learn(data,destination,type_of_forest,learn_num,tree_num)
    type_of_forest_name="随机森林" if type_of_forest=="RandomForestClassifier" else "梯度提升"
    MLPstruct="100 50" if request.form.get("MLP_num") == '' else request.form.get("MLP_num")
    MLP_num=MLPstruct.split(" ")
    MLP_num=[int(k) for k in MLP_num]
    MLP_func=request.form.get("opt")
    MLP_you=request.form.get("solver")
    net_obj_list=netMLP(data,destination,MLP_num,MLP_func,MLP_you)
    MLP_dict={"indentity":"线性激活","logistic":"逻辑激活函数","tanh":'双曲正切激活函数',"relu":"修正线性单元"}
    solve_dict={"lbfgs":"LBFGS","sgd":"随机梯度下降","adam":"自适应矩估计"}
    func_name=MLP_dict[MLP_func]
    you_name=solve_dict[MLP_you]

    svc_num=1.0 if request.form.get("SVC_num")=='' else request.form.get("SVC_num")
    svc_func=request.form.get("SVC_type")
    svc_pro= True if request.form.get("SVC_pro") =="on" else False
    svc_func_name={"linear":"线性核","poly":"多项式核","rbf":"高斯核","sigmoid":"Sigmoid核","precomputed":"预计算核"}
    svc_pro_name="" if svc_pro else "不"


    return render_template('answer.html',dataname=dataname,BYS=bys_obj_list,KNN=Knn_obj_list,k=k,detree=de_tree_obj_list,dedeep=decision_deep,
                           one=togeter_obj_list,together_name=type_of_forest_name,learn_num=learn_num,tree_num=tree_num,
                           Net=net_obj_list,Net_num=len(MLP_num),func_name=func_name,you_name=you_name,
                           svc=SVC_(data,destination,svc_num,svc_func,svc_pro),svc_func_name=svc_func_name[svc_func],svc_pro_name=svc_pro_name,C=svc_num)


#——————————————————源代码操作结束，下面是使用sklearn方法————————————————————————
@app.route('/display_sk',methods=['GET','POST'])
def display_sk():
    data = f[0]
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    data = pd.DataFrame(data)
    destination = int(request.form.get('destination'))
    k = request.form.get("K")
    decision_deep = request.form.get("decision_deep")
    if decision_deep == '':
        de_tree_obj_list = decision_tree_sk(data, destination, 3)
        decision_deep = 3
    else:
        de_tree_obj_list = decision_tree_sk(data, destination, decision_deep)
    if k == '' or int(k) <= 0:
        Knn_obj_list = K_neighbor_sk(data, destination, 5)
        k = 5
    else:
        Knn_obj_list = K_neighbor_sk(data, destination, int(k))
    bys_obj_list = BYS_sk(data, destination)
    type_of_forest = "RandomForestClassifier" if request.form.get("option") is None else request.form.get("option")
    learn_num = 100 if request.form.get("learn_num") == "" else request.form.get("learn_num")
    tree_num = 3 if request.form.get("tree_num") == "" else request.form.get("tree_num")
    togeter_obj_list = together_learn_sk(data, destination, type_of_forest, learn_num, tree_num)
    type_of_forest_name = "随机森林" if type_of_forest == "RandomForestClassifier" else "梯度提升"
    MLPstruct = "100 50" if request.form.get("MLP_num") == '' else request.form.get("MLP_num")
    MLP_num = MLPstruct.split(" ")
    MLP_num = [int(k) for k in MLP_num]
    MLP_func = request.form.get("opt")
    MLP_you = request.form.get("solver")
    net_obj_list = netMLP_sk(data, destination, MLP_num, MLP_func, MLP_you)
    MLP_dict = {"indentity": "线性激活", "logistic": "逻辑激活函数", "tanh": '双曲正切激活函数', "relu": "修正线性单元"}
    solve_dict = {"lbfgs": "LBFGS", "sgd": "随机梯度下降", "adam": "自适应矩估计"}
    func_name = MLP_dict[MLP_func]
    you_name = solve_dict[MLP_you]

    svc_num = 1.0 if request.form.get("SVC_num") == '' else request.form.get("SVC_num")
    svc_func = request.form.get("SVC_type")
    svc_pro = True if request.form.get("SVC_pro") == "on" else False
    svc_func_name = {"linear": "线性核", "poly": "多项式核", "rbf": "高斯核", "sigmoid": "Sigmoid核",
                     "precomputed": "预计算核"}
    svc_pro_name = "" if svc_pro else "不"

    return render_template('answer_sklearn.html', dataname="", BYS=bys_obj_list, KNN=Knn_obj_list, k=k, detree=de_tree_obj_list,
                           dedeep=decision_deep,
                           one=togeter_obj_list, together_name=type_of_forest_name, learn_num=learn_num,
                           tree_num=tree_num,
                           Net=net_obj_list, Net_num=len(MLP_num), func_name=func_name, you_name=you_name,
                           svc=SVC__sk(data, destination, svc_num, svc_func, svc_pro),
                           svc_func_name=svc_func_name[svc_func], svc_pro_name=svc_pro_name, C=svc_num)
@app.route('/display2_sklearn',methods=['GET','POST'])
def display2_sklearn():
    data = f[1]
    dataq=f[1]
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    data = pd.DataFrame(data)
    goal=int(request.form.get('goal'))
    label=set()
    for i in range(0,len(data.iloc[:,goal])):
        label.add(data.iloc[i,goal])
    label=list(label)
    sorted(label)
    Label=dict()
    for i in range(0,len(label)):
        Label[label[i]]=i
    for i in range(0, len(data.iloc[:, goal])):
        data.iloc[i,goal]=int(Label[data.iloc[i,goal]])
    dataName=[]
    for i in range(0,data.shape[1]):
        dataName.append(i)
    data.columns=dataName
    print(Label)
    print("*"*100)
    print(data)

    print(data.dtypes)



    VTnum=0.2 if request.form.get("VT")=='' else request.form.get("VT")
    VT_list=VT_sk(data, goal, VTnum, dataq)
    saving_list = []
    dataqq = dataq.drop(columns=dataq.columns[goal])
    for i in range(0, len(VT_list[4])):
        if VT_list[4][i] == True:
            saving_list.append(dataqq.columns.tolist()[i])
    VT_list[0].columns = saving_list
    VT_list[1].columns = [dataq.columns.tolist()[goal]]
    vtx=VT_list[0].head()
    vtx=vtx.to_html(index=False, classes='table table-striped')
    vty = VT_list[1].head()
    vty=vty.to_html(index=False, classes='table table-striped')
    # vtx=VT_list[0][:,6].to_html(index=False, classes='table table-striped')
    # vty = VT_list[1][:,6].to_html(index=False, classes='table table-striped')
    name_list=dataq.columns.tolist()
    name_dict={}
    for i in data.columns.tolist():
        name_dict[data.columns.tolist()[i]]=name_list[i]
    new_dict={}
    for k,v in VT_list[3].items():
        new_name=name_list[k]
        new_dict[new_name]=v
    VT_list[3]=new_dict
    vtdata=pd.concat([VT_list[0],VT_list[1]],axis=1)
    all_data["vt"]=vtdata


    SKnum=int(np.floor(data.shape[1]/2)) if request.form.get("SK")=='' else request.form.get("SK")
    SKfunc=request.form.get("function")
    SK_list=SK_sk(data, goal, SKfunc, SKnum, dataq)
    sk_saving=[]
    for i in range(0,len(dataqq.columns.tolist())):
        if SK_list[4][i]==True:
            sk_saving.append(dataq.columns.tolist()[i])
    SK_list[0].columns = sk_saving
    SK_list[1].columns = [dataq.columns.tolist()[goal]]
    skx=SK_list[0].head()
    sky=SK_list[1].head()
    skx=skx.to_html(index=False, classes='table table-striped')
    sky=sky.to_html(index=False, classes='table table-striped')
    sk_dict={}
    sk_p={}
    for i in range(0,len(saving_list)):
        sk_dict[saving_list[i]]=SK_list[2][i]
        sk_p[saving_list[i]]=SK_list[3][i]
    SK_list[2]=sk_dict
    SK_list[3]=sk_p
    skdata = pd.concat([SK_list[0], SK_list[1]], axis=1)
    all_data['sk']=skdata




    RFE_num=int(np.floor(data.shape[1]/2)) if request.form.get("now_feature")=='' else request.form.get("now_feature")
    rfe_obj=request.form.get("base_obj")
    step=1 if (request.form.get("step")=="" or request.form.get("step")>data.shapes[1]) else request.form.get("step")
    RFE_list=RFE__sk(data, goal, RFE_num, rfe_obj, step)
    RFE_list[1].columns = [dataq.columns.tolist()[goal]]
    rfe_name=[]
    for i in range(0, len(dataqq.columns.tolist())):
        if RFE_list[2][i]:
            rfe_name.append(dataq.columns.tolist()[i])
    RFE_list[0].columns=rfe_name

    rank={}
    for i in range(0,len(RFE_list[3])):
        rank[i] = dataq.columns.tolist()[i] + "在第" + str(RFE_list[3][i]) + "次迭代筛选时被选中"
    ca=""
    for i in range(0, len(RFE_list[3])):
        ca+="特征"+str(rank[i])+"<br>"

    # now_name = [rfe_name[i] for i, value in enumerate(RFE_list[2]) if value]
    rfex=RFE_list[0].head().to_html(index=False, classes='table table-striped')
    rfey=RFE_list[1].head().to_html(index=False, classes='table table-striped')
    rfedata=pd.concat([RFE_list[0],RFE_list[1]],axis=1)
    all_data['rfe']=rfedata
    data_name['rfe']="基于包裹式策略下的特征选择过滤数据的"


    Lanum=1.0 if request.form.get("Lassonum")=='' else request.form.get("Lassonum")==''
    Lamost=1000 if request.form.get("Lassoround")=='' else request.form.get("Lassoround")
    Latol=0.0001 if request.form.get("tol")== '' else request.form.get("tol")
    Lani=True if request.form.get("ni")=="on" else False
    LA=Lasso__sk(data, goal, Lanum, Lamost, Latol, Lani, dataq)
    LAx=LA[0].head().to_html(index=False, classes='table table-striped')
    LAy=LA[1].head().to_html(index=False, classes='table table-striped')
    LA[4]=LA[4].tolist()
    LAdata=pd.concat([LA[0],LA[1]],axis=1)
    all_data['lasso']=LAdata
    data_name['lasso']="基于嵌入式策略下的Lasso回归过滤数据"

    lnum=1.0 if request.form.get('lnum')=='' else request.form.get('lnum')
    lround=1000 if request.form.get("lround")=='' else request.form.get("lround")
    ltol=0.0001 if request.form.get("ltol")=='' else request.form.get("ltol")
    lni = True if request.form.get("lni") == "on" else True
    lgui=False if request.form.get("lni")=="off" else True
    limit=1 if request.form.get("llimit")=='' else request.form.get('llimit')
    LIN=ridge_sk(data, goal, lnum, lround, ltol, lni, lgui, dataq, limit)
    LINx=LIN[0].head().to_html(index=False, classes='table table-striped')
    LINy=LIN[1].head().to_html(index=False, classes='table table-striped')
    LINnum={}
    for i in range(0,len(LIN[2])):
        LINnum[dataqq.columns.tolist()[i]]=LIN[2][i]
    LINdata=pd.concat([LIN[0],LIN[1]],axis=1)
    all_data['lin']=LINdata
    data_name['lin']="基于嵌入式策略下的岭回归特征选择过滤数据"

    softnum = 1.0 if request.form.get('softnum') == '' else float(request.form.get('softnum'))
    softround = 1000 if request.form.get("softround") == '' else int(request.form.get("softround"))
    softtol = 0.0001 if request.form.get("softtol") == '' else float(request.form.get("softtol"))
    softni = True if request.form.get("softni") == "on" else True
    softgui = False if request.form.get("softni") == "off" else True
    softimit = 0.3 if request.form.get("softlimit") == '' else float(request.form.get('softlimit'))
    softL=0.5 if request.form.get("softL1")=='' else request.form.get("softL1")
    softL=float(softL)
    if softL<=0:
        softL=0
    elif softL>=1:
        softL=1
    ELS=elastic_sk(data, goal, softnum, softround, softL, softtol, softni, softgui, dataq, softimit)
    ELSx=ELS[0].head().to_html(index=False, classes='table table-striped')
    ELSy=ELS[1].head().to_html(index=False, classes='table table-striped')
    ELSdata=pd.concat([ELS[0],ELS[1]],axis=1)
    all_data['els']=ELSdata
    data_name['els']='基于嵌入式策略下的弹性网特征选择过滤数据'




    return render_template("answer2_sklearn.html",VT=VT_list,vtx=vtx,vty=vty,vt_head_name=dataq.columns.tolist(),
                           SK=SK_list,skx=skx,sky=sky,
                           RFE=RFE_list,rfe_name=rfe_name,rfex=rfex,rfey=rfey,ca=ca,
                           LA=LA,LAx=LAx,LAy=LAy,
                           LIN=LIN,LINx=LINx,LINy=LINy,LINnum=LINnum,
                           ELS=ELS,ELSx=ELSx,ELSy=ELSy)
@app.route('/display3_sklearn',methods=['GET','POST'])
def display3_sklearn():
    data = f[0]
    dataq = f[1]
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    data = pd.DataFrame(data)
    aim=int(request.form.get("aim"))
    num=int(data.shape[1]/2) if request.form.get("num")=='' else request.form.get("num")
    white=True if request.form.get("white")=='on' else False
    solve=request.form.get("solve")
    pcalist=PCA__sk(data, aim, num, white, solve, dataq)
    dataqq = dataq.drop(columns=dataq.columns[aim])
    pcax=pcalist[0].head().to_html(index=False, classes='table table-striped')
    pcay=pcalist[1].head().to_html(index=False, classes='table table-striped')
    pcadata=pd.DataFrame(pcalist[2],columns=dataqq.columns.tolist())
    pcadata=pcadata.to_html(index=False, classes='table table-striped')
    pcalist[6] = np.reshape(pcalist[6], (1, len(pcalist[6])))
    pcalist[6]=pd.DataFrame(pcalist[6],columns=dataqq.columns.tolist())
    pcalist[6]=pcalist[6].to_html(index=False, classes='table table-striped')
    return render_template("answer3_sklearn.html",pca=pcalist,pcax=pcax,pcay=pcay,pcadata=pcadata)

@app.route('/display4_sklearn',methods=['GET','POST'])
def display4_sklearn():
    data = f[0]
    dataq = f[1]
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    first = int(request.form.get("first"))
    second = int(request.form.get("second"))
    aim=int(request.form.get("aim"))
    data=data.iloc[:,[first,second,aim]]
    data = pd.DataFrame(data)
    dataqq = dataq.iloc[:,[first,second,aim]]
    data.columns = dataqq.columns
    KCnum=4 if request.form.get('KCnum')=='' else int(request.form.get('KCnum'))
    Kfunc=request.form.get('Kfunc')
    KNseed=10 if request.form.get('KNseed')=='' else int(request.form.get('KNseed'))
    KNd=300 if request.form.get("KNd")=='' else int(request.form.get("KNd"))
    KNtol=0.0001 if request.form.get("KNtol")=='' else float(request.form.get("KNtol"))
    KN=KN_cluster_sk(data, first, second, KCnum, Kfunc, KNseed, KNd, KNtol)


    ACnum=4 if request.form.get("ACnum")=='' else int(request.form.get("ACnum"))
    ACdis=request.form.get("ACdistance")
    fulltree='auto' if request.form.get("fulltree")=='auto' else True if request.form.get("fulltree")=='on' else False
    AC=AC__sk(data, ACnum, ACdis, fulltree)

    EMnum=4 if request.form.get("EMnum")=='' else int(request.form.get("EMnum"))
    EMfunc=request.form.get("type_of_EM")
    EMd=100 if request.form.get("EMd")=='' else int(request.form.get("EMd"))
    EMtol=0.001 if request.form.get("EMtol")=='' else float(request.form.get("EMtol"))
    EM=EM__sk(data, EMnum, EMfunc, EMd, EMtol)

    DBr=0.05 if request.form.get("DBr")=='' else float(request.form.get("DBr"))
    DBcenter=15 if request.form.get("DBcenter")=='' else int(request.form.get("DBcenter"))
    alg=request.form.get("DBalg")

    DB=DB__sk(data, DBr, DBcenter, alg)
    return render_template('answer4.html_sklearn',kn=KN,knnum=KCnum,Kfunc=Kfunc,KNseed=KNseed,KNd=KNd,KNtol=KNtol,
                           ac=AC,em=EM,DB=DB)


@app.route('/datago_sklearn',methods=['GET','POST'])
def datago_sklearn():
    data=all_data[request.form.get("type_of_data")]
    dataname=data_name[request.form.get("type_of_data")]
    dataname+="的"
    destination=-1
    if data is None:
        flash('数据未正确加载')
        return redirect(request.url)
    k=request.form.get("K")
    decision_deep=request.form.get("decision_deep")
    if decision_deep=='':
        de_tree_obj_list=decision_tree_sk(data, destination, 3)
        decision_deep=3
    else:
        de_tree_obj_list = decision_tree_sk(data, destination, decision_deep)
    if k=='' or int(k)<=0:
        Knn_obj_list=K_neighbor_sk(data, destination, 5)
        k=5
    else:
        Knn_obj_list=K_neighbor_sk(data, destination, int(k))
    bys_obj_list=BYS_sk(data, destination)
    type_of_forest="RandomForestClassifier" if request.form.get("option") is None else request.form.get("option")
    learn_num=100 if request.form.get("learn_num")=="" else request.form.get("learn_num")
    tree_num = 3 if request.form.get("tree_num") == "" else request.form.get("tree_num")
    togeter_obj_list=together_learn_sk(data, destination, type_of_forest, learn_num, tree_num)
    type_of_forest_name="随机森林" if type_of_forest=="RandomForestClassifier" else "梯度提升"
    MLPstruct="100 50" if request.form.get("MLP_num") == '' else request.form.get("MLP_num")
    MLP_num=MLPstruct.split(" ")
    MLP_num=[int(k) for k in MLP_num]
    MLP_func=request.form.get("opt")
    MLP_you=request.form.get("solver")
    net_obj_list=netMLP_sk(data, destination, MLP_num, MLP_func, MLP_you)
    MLP_dict={"indentity":"线性激活","logistic":"逻辑激活函数","tanh":'双曲正切激活函数',"relu":"修正线性单元"}
    solve_dict={"lbfgs":"LBFGS","sgd":"随机梯度下降","adam":"自适应矩估计"}
    func_name=MLP_dict[MLP_func]
    you_name=solve_dict[MLP_you]

    svc_num=1.0 if request.form.get("SVC_num")=='' else request.form.get("SVC_num")
    svc_func=request.form.get("SVC_type")
    svc_pro= True if request.form.get("SVC_pro") =="on" else False
    svc_func_name={"linear":"线性核","poly":"多项式核","rbf":"高斯核","sigmoid":"Sigmoid核","precomputed":"预计算核"}
    svc_pro_name="" if svc_pro else "不"


    return render_template('answer.html_sklearn', dataname=dataname, BYS=bys_obj_list, KNN=Knn_obj_list, k=k, detree=de_tree_obj_list, dedeep=decision_deep,
                           one=togeter_obj_list, together_name=type_of_forest_name, learn_num=learn_num, tree_num=tree_num,
                           Net=net_obj_list, Net_num=len(MLP_num), func_name=func_name, you_name=you_name,
                           svc=SVC__sk(data, destination, svc_num, svc_func, svc_pro), svc_func_name=svc_func_name[svc_func], svc_pro_name=svc_pro_name, C=svc_num)




#——————————————————下面是报错页面————————————————————————————

@app.errorhandler(404)
def not_found(e):#这个e一定要加到参数上
    print(e)
    return render_template('error.html')
@app.errorhandler(500)
def not_found2(e):
    print(e)
    return render_template('error2.html')
@app.errorhandler(501)
def not_found3(e):
    return "本地端不支持这个请求……"
if __name__=='__main__':
    app.run(host="127.0.0.1",port=5000)










