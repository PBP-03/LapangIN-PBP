from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from .models import User, Venue, Court, SportsCategory


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Username atau Email',
            'id': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Password',
            'id': 'password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Email',
            'id': 'email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Nama Depan',
            'id': 'first_name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Nama Belakang',
            'id': 'last_name'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Username',
            'id': 'username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Password',
            'id': 'password1'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Konfirmasi Password',
            'id': 'password2'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Nomor Telepon (Opsional)',
            'id': 'phone_number'
        })
    )
    role = forms.ChoiceField(
        choices=[('user', 'User/Penyewa'), ('mitra', 'Mitra/Pemilik Lapangan')],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'id': 'role'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'phone_number', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove labels for cleaner look
        for field_name in self.fields:
            self.fields[field_name].label = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class VenueForm(forms.ModelForm):
    """Form for creating and editing venues"""
    
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Nama Venue',
            'id': 'name'
        })
    )
    
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Alamat Lengkap',
            'rows': 3,
            'id': 'address'
        })
    )
    
    location_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Google Maps URL (Opsional)',
            'id': 'location_url'
        })
    )
    
    contact = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Nomor Kontak',
            'id': 'contact'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Deskripsi Venue',
            'rows': 4,
            'id': 'description'
        })
    )
    
    number_of_courts = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Jumlah Lapangan',
            'min': '1',
            'id': 'number_of_courts'
        })
    )
    
    class Meta:
        model = Venue
        fields = ['name', 'address', 'location_url', 'contact', 'description', 'number_of_courts']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make labels more user-friendly
        self.fields['name'].label = 'Nama Venue'
        self.fields['address'].label = 'Alamat'
        self.fields['location_url'].label = 'URL Lokasi (Google Maps)'
        self.fields['contact'].label = 'Nomor Kontak'
        self.fields['description'].label = 'Deskripsi'
        self.fields['number_of_courts'].label = 'Jumlah Lapangan'


class CourtForm(forms.ModelForm):
    """Form for creating and editing courts"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Nama Lapangan (contoh: Lapangan 1, Court A)',
            'id': 'name'
        })
    )
    
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'id': 'venue'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=SportsCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'id': 'category'
        })
    )
    
    price_per_hour = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Harga per Jam (Rp)',
            'min': '0',
            'step': '1000',
            'id': 'price_per_hour'
        })
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-primary-600 bg-neutral-100 border-neutral-300 rounded focus:ring-primary-500 focus:ring-2',
            'id': 'is_active'
        })
    )
    
    maintenance_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Catatan Maintenance (Opsional)',
            'rows': 3,
            'id': 'maintenance_notes'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 focus:outline-none transition-all duration-200',
            'placeholder': 'Deskripsi Lapangan (Opsional)',
            'rows': 3,
            'id': 'description'
        })
    )
    
    class Meta:
        model = Court
        fields = ['venue', 'name', 'category', 'price_per_hour', 'is_active', 'maintenance_notes', 'description']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter venues to only show the user's venues (if user is a mitra)
        if user and user.role == 'mitra':
            self.fields['venue'].queryset = Venue.objects.filter(owner=user)
        
        # Set labels
        self.fields['venue'].label = 'Venue'
        self.fields['name'].label = 'Nama Lapangan'
        self.fields['category'].label = 'Kategori Olahraga'
        self.fields['price_per_hour'].label = 'Harga per Jam (Rp)'
        self.fields['is_active'].label = 'Aktif'
        self.fields['maintenance_notes'].label = 'Catatan Maintenance'
        self.fields['description'].label = 'Deskripsi Lapangan'

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border', 'placeholder': 'Nama depan'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border', 'placeholder': 'Nama belakang'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border', 'placeholder': 'Nomor telepon'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border', 'placeholder': 'Alamat', 'rows':3}),
        }