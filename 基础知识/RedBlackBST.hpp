#define RED true
#define BLACK false

template<typename Key,typename Value>
class Node 
{
public:
    Key key;
    Value value;
    Node* left, right;
    int N;
    bool color;
    Node(Key _key, Value _value, bool _color): key(_key), value(_value), left(nullptr), right(nullptr), color(_color){};
};

template<typename Key,typename Value>
class RedBlackBST
{
public:
    typedef Node<Key, Value> node;
    node root;
    void put(Key _key, Value _value) {
        root = put(root, _key, _value);
        root->color = BLACK;
    };

    node* min() {}
    node* max() {}
    node* get(node* h, Key key) {}
    void deleteMin(node* h) {
        if (!isRed(root->left) && !isRed(root->right))
            root->color = RED;
        root = _deleteMin(root);
        if (!isEmpty()) root->color = BLACK;
    }
    void deleteMax(node* h) {
        if (!isRed(root->left && !isRed(root->right)))
            root->color = RED;
        root = _deleteMax(root);
        if (!isEmpty())  root->color = BLACK;       
    }
    void delete_node(Key key) {
        if (!isRed(root->left && !isRed(root->right)))
            root->color = RED;
        root = _delete_node(root, Key);
        if (!isEmpty()) root->color = BLACK;
    }
    bool isEmpty() {
        return false;
    }

    
private:
    // 左旋
    node* rotateLeft(node* h) {
        node* x = h->right;
        h->right = x->left;
        x->left = h;
        x->color = h->color;
        h->color = RED;
        x.N = h.N;
        h.N = 1 + size(h->left) + size(h->right);
        return x;
    };
    // 右旋
    node* rotateRight(node* h) {
        node* x = h->left;
        h->left = x->right;
        x->right = h;
        x->color = h->color;
        h->color = RED;
        x.N = h.N;
        h.N = 1 + size(h->left) + size(h->right);
        return x;
    };
    // 变色
    node* flipColors(node* h) {
        h->left->color = BLACK;
        h->right->color = BLACK;
        h->color = RED;
    };
    node* put(node* h, Key _key, Value _value) {
        if (nullptr == h) 
            return new Node(_key, _value, RED);
        int h_val = h->value;
        if (h < h_val) h->left = put(h->left, _key, _value);
        else if (h > h_val) h->right = put(h->right, _key, _value);
        else  h->value = _value;  // 相等

        // 调整
        if (isRed(h->right) && !isRed(h->left)) h = rotateLeft(h);
        if (!isRed(h->right) && isRed(h->left)) h = rotateRight(h);
        if (isRed(h->right) && isRed(h->left)) flipColors(h);
    
        h->N = size(h->left) + size(h->right) + 1;
        return h;
    };
    bool isRed(node* x) {
        if (!x) return false;
        return x->color == RED;
    }
    int size(node* h) {
        if (h == nullptr) return 0;
        return h->N;
    }
    // delete
    // +-------------------------------------------+
    // +--------------辅助函数-----------------------+
    // +-------------------------------------------+
    node* moveRedLeft(node* h) {
        mflipColors(h); // 不同
        if (isRed(h->right->left)) {
            h->right = rotateRight(h->right);
            h = rotateLeft(h);
        }
        return h;
    }
    node* moveRedRight(node* h) {
        mflipColors(h); // 不同
        if (!isRed(h->left->left)) {
            h = rotateRight(h);
        }
        return h;
    }
    node* _deleteMin(node* h) {
        if (!h->left)
            return nullptr;
        if (!isRed(h->left) && !isRed(h->left->left))
            h = moveRedLeft(h);
        h->left = _deleteMin(h->left);
        return balance(h);
    }  
    node* _deleteMax(node* h) {
        if (isRed(h->left))
            h = rotateRight(h);
        if (!h->right)
            return nullptr;
        if (!isRed(h->right) && !isRed(h->right->left))
            h = moveRedRight(h);  // 出现
        h->right = _deleteMax(h->right);
        return balance(h);
    }

    node* balance(node* h) {
        if (isRed(h->right)) h = rotateLeft(h);
        if (isRed(h->right) && !isRed(h->left)) h = rotateLeft(h);
        if (!isRed(h->right) && isRed(h->left)) h = rotateRight(h);
        if (isRed(h->right) && isRed(h->left)) flipColors(h);
    
        h->N = size(h->left) + size(h->right) + 1;
        return h;
    }

    node* _delete_node(node* h, Key key) {
        if (key < h->key) {
            if (!isRed(h->left) && !isRed(h->left->left)) {
                h = moveRedLeft(h);
            }
            h->left = _delete_node(h->left, key);
        } else {
            if (isRed(h->left)) 
                h = rotateRight(h);
            if (key == h->key && !h->right) {

                return nullptr; // 这里需要回收一下
            }
            if (key == h->key) {
                h->value = get(h->right, min(h->right)->key);
                h->key = min(h->right);
                h->right = _deleteMin(h->right);
            }
            else h->right = delete(h->right, key);
        }
        return balance(h);
    }
};
 