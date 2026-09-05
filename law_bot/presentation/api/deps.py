from database.repo import CategoryRepo, ProductRepo, AnswerRepo


def category_repo():
    return CategoryRepo()


def product_repo():
    return ProductRepo()


def answer_repo():
    return AnswerRepo()