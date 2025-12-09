from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Avg
import json

from app.venues.models import Venue
from app.bookings.models import Booking
from app.reviews.models import Review

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_venue_reviews(request, venue_id):
    """API endpoint for listing and creating venue reviews"""
    try:
        venue = Venue.objects.get(pk=venue_id)
    except Venue.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Venue not found'}, status=404)

    if request.method == "GET":
        # Get all reviews for this venue
        reviews = Review.objects.filter(
            booking__court__venue=venue
        ).select_related('booking__user').order_by('-created_at')

        reviews_data = [{
            'id': str(review.id),
            'user': review.booking.user.username,
            'user_full_name': review.booking.user.get_full_name(),
            'rating': float(review.rating),
            'comment': review.comment,
            'created_at': review.created_at.isoformat()
        } for review in reviews]

        # Calculate average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        return JsonResponse({
            'status': 'success',
            'data': {
                'reviews': reviews_data,
                'avg_rating': float(avg_rating),
                'total_reviews': len(reviews_data)
            }
        })

    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

        try:
            data = json.loads(request.body)
            rating = data.get('rating')
            comment = data.get('comment', '')

            if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Rating harus antara 1 dan 5'
                }, status=400)

            # Find the most recent completed booking for this user at this venue
            booking = Booking.objects.filter(
                court__venue=venue,
                user=request.user,
                booking_status='completed'
            ).exclude(
                review__isnull=False  # Exclude bookings that already have reviews
            ).order_by('-booking_date').first()

            if not booking:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Anda harus menyelesaikan booking terlebih dahulu untuk memberikan review'
                }, status=400)

            # Create the review
            review = Review.objects.create(
                booking=booking,
                rating=rating,
                comment=comment
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Review berhasil ditambahkan',
                'data': {
                    'id': str(review.id),
                    'rating': float(review.rating),
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def api_manage_review(request, review_id):
    """API endpoint for updating and deleting reviews"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login required'}, status=401)

    try:
        review = Review.objects.get(pk=review_id)
        
        # Check if user owns this review
        if review.booking and review.booking.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

        if request.method == "PUT":
            data = json.loads(request.body)
            rating = data.get('rating')
            comment = data.get('comment', review.comment)

            if rating is not None:
                if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Rating harus antara 0 dan 5'
                    }, status=400)
                review.rating = rating

            review.comment = comment
            review.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Review berhasil diupdate',
                'data': {
                    'id': str(review.id),
                    'rating': float(review.rating),
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                }
            })

        elif request.method == "DELETE":
            review.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Review berhasil dihapus'
            })

    except Review.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Review not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
