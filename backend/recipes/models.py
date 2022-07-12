from django.contrib.auth import get_user_model
from django.db import models

from recipes.validators import LIMIT_MIN_INT, validate_hex_code

User = get_user_model()


def user_image_upload_path(instance, filename):
    return 'recipes/images/{0}/{1}'.format(instance.user.username, filename)


class Tags(models.Model):
    name = models.CharField('tag name', max_length=50, unique=True)
    color = models.CharField('color HEX code', max_length=7, unique=True,
                             validators=[validate_hex_code])
    slug = models.SlugField('slug', max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField('ingredient name', max_length=50)
    measurement_unit = models.CharField('measurement unit', max_length=10)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'ingredients'
        indexes = [
            models.Index(
                name='ingredients_idx',
                fields=['name'],
                include=['measurement_unit']
            )
        ]
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredients_unit')
        ]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='ingredient name',
        related_name='ingredient_in_recipes',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        'amount of ingredients', validators=LIMIT_MIN_INT, null=True)

    def __str__(self):
        return self.ingredient


class Recipes(models.Model):
    name = models.CharField('recipe name', max_length=100)
    author = models.ForeignKey(
        User,
        verbose_name='author',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='tag name',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        IngredientInRecipe,
        verbose_name='ingredients_in_recipe',
        related_name='recipes',
    )
    text = models.TextField('recipe description')
    image = models.ImageField('dish image', upload_to=user_image_upload_path)
    cooking_time = models.PositiveSmallIntegerField(validators=LIMIT_MIN_INT)

    class Meta:
        verbose_name_plural = 'recipes'

    def __str__(self):
        return self.name


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['follower', 'author'],
                                               name='unique_users')]

    def __str__(self):
        return self.follower


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='fav_user')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                               related_name='fav_recipe')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_fav_recipes')]

    def __str__(self):
        return self.user


class RecipeInCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='buyer')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                               related_name='recipe_in_cart')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_recipe_in_cart')
        ]

    def __str__(self):
        return self.user
